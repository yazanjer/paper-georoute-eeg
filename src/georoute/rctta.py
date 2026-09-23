"""Online, backprop-free test-time adaptation for EEG decoders.

RCTTA (Riemannian Co-Training Test-Time Adaptation)
---------------------------------------------------
A source-trained decoder (e.g. an EEG foundation model) gives class probabilities
p_fm for each incoming trial.  In parallel, RCTTA builds a *target-specific*
Riemannian classifier from the unlabeled stream itself:

  1. trial covariances (8-30 Hz, OAS) are re-centred at the running Riemannian
     mean of the target stream and mapped to its tangent space;
  2. class prototypes in that tangent space are estimated by soft EM, using the
     fused posteriors of all trials seen so far as responsibilities;
  3. geometry posteriors p_geo = softmax(-||t - mu_c||^2 / tau) are fused with
     the decoder:  q  ∝  p_fm * p_geo^lambda_eff,
     lambda_eff = lambda * n / (n + n0)  (geometry is trusted as evidence accrues).

Only past + current trials are used (predict-then-update); no gradients, no
source data, no labels.  Everything here is numpy / pyriemann.
"""
from __future__ import annotations

import numpy as np
from scipy.signal import butter, sosfiltfilt
from pyriemann.estimation import Covariances
from pyriemann.utils.mean import mean_riemann
from pyriemann.utils.tangentspace import tangent_space

SFREQ = 200


def softmax(z, axis=1):
    z = z - z.max(axis, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis, keepdims=True)


def bandpass(X, lo=8.0, hi=30.0, fs=SFREQ, order=4):
    sos = butter(order, [lo, hi], btype="band", fs=fs, output="sos")
    return sosfiltfilt(sos, X, axis=-1).astype(np.float64)


def covs(X):
    return Covariances(estimator="oas").fit_transform(np.asarray(X, dtype=np.float64))


# ---------------------------------------------------------------- incremental EA
class OnlineEA:
    """Euclidean alignment with a running arithmetic-mean reference (T-TIME style)."""

    def __init__(self):
        self.S, self.n = None, 0

    def __call__(self, Xb):
        C = covs(Xb)
        self.S = C.sum(0) if self.S is None else self.S + C.sum(0)
        self.n += len(C)
        R = self.S / self.n
        w, V = np.linalg.eigh(R)
        W = (V / np.sqrt(np.maximum(w, 1e-10))) @ V.T
        return np.einsum("ij,njt->nit", W, Xb).astype(np.float32)


# ---------------------------------------------------------------- baselines
def t3a_stream(feats_batches, W, b, filter_k=20, temp=0.1):
    """Online T3A (Iwasawa & Matsuo, 2021). Yields class probabilities per batch."""
    n_cls = W.shape[0]
    norm = lambda a: a / (np.linalg.norm(a, axis=1, keepdims=True) + 1e-8)
    sup_z, sup_y, sup_ent = norm(W.copy()), np.arange(n_cls), np.zeros(n_cls)
    for z in feats_batches:
        p = softmax(z @ W.T + b)
        ent = -(p * np.log(p + 1e-8)).sum(1)
        sup_z = np.vstack([sup_z, norm(z)])
        sup_y = np.concatenate([sup_y, p.argmax(1)])
        sup_ent = np.concatenate([sup_ent, ent])
        keep = []
        for c in range(n_cls):
            ic = np.where(sup_y == c)[0]
            keep.extend(ic[np.argsort(sup_ent[ic])[:filter_k]])
        keep = np.array(sorted(keep))
        sup_z, sup_y, sup_ent = sup_z[keep], sup_y[keep], sup_ent[keep]
        protos = np.stack([sup_z[sup_y == c].mean(0) for c in range(n_cls)])
        yield softmax((norm(z) @ norm(protos).T) / temp)


def lame(p, feats, k=5, n_iter=10):
    """LAME (Boudiaf et al., CVPR 2022): Laplacian-adjusted max-likelihood on a batch."""
    n = len(p)
    if n < 2:
        return p
    f = feats / (np.linalg.norm(feats, axis=1, keepdims=True) + 1e-8)
    S = f @ f.T
    np.fill_diagonal(S, -np.inf)
    kk = min(k, n - 1)
    W = np.zeros_like(S)
    idx = np.argsort(-S, axis=1)[:, :kk]
    rows = np.repeat(np.arange(n), kk)
    W[rows, idx.ravel()] = 1.0
    W = np.maximum(W, W.T)
    logp = np.log(p + 1e-8)
    z = p.copy()
    for _ in range(n_iter):
        z = softmax(logp + W @ z)
    return z


# ---------------------------------------------------------------- RCTTA
class RCTTA:
    def __init__(self, n_classes, lam=1.0, n0=20, em_iters=5, band=(8.0, 30.0),
                 recenter=True, conf_weight=True):
        self.K, self.lam, self.n0, self.em_iters = n_classes, lam, n0, em_iters
        self.band, self.recenter, self.conf_weight = band, recenter, conf_weight
        self.C = None          # (n, ch, ch) covariances seen so far
        self.P = None          # (n, K) decoder posteriors seen so far

    def _tangent(self):
        ref = mean_riemann(self.C) if self.recenter else np.eye(self.C.shape[1])
        T = tangent_space(self.C, ref)
        return T / (np.linalg.norm(T, axis=1, keepdims=True).mean() + 1e-12)

    def step(self, Xb, p_fm):
        """Xb: raw (aligned) batch (b, ch, t); p_fm: (b, K). Returns fused posteriors (b, K)."""
        Xf = bandpass(Xb, *self.band) if self.band else np.asarray(Xb, np.float64)
        Cb = covs(Xf)
        self.C = Cb if self.C is None else np.concatenate([self.C, Cb])
        self.P = p_fm if self.P is None else np.concatenate([self.P, p_fm])
        n = len(self.C)
        lam_eff = self.lam * n / (n + self.n0)
        if n < 2 * self.K or lam_eff <= 0:
            return p_fm
        T = self._tangent()
        logpf = np.log(self.P + 1e-8)
        q = self.P.copy()
        for _ in range(self.em_iters):
            w = q * (q.max(1, keepdims=True) if self.conf_weight else 1.0)
            mu = (w.T @ T) / (w.sum(0)[:, None] + 1e-8)                  # (K, D)
            d2 = ((T[:, None, :] - mu[None]) ** 2).sum(-1)               # (n, K)
            tau = np.median(d2) + 1e-8
            logpg = np.log(softmax(-d2 / tau) + 1e-8)
            q = softmax(logpf + lam_eff * logpg)
        self.last_geo = softmax(-d2 / tau)[-len(Xb):]
        return q[-len(Xb):]
