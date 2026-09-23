"""Backprop-free test-time prototype adjustment (T3A, Iwasawa & Matsuo 2021)."""
from __future__ import annotations

import numpy as np


def _softmax(z):
    z = z - z.max(1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(1, keepdims=True)


def t3a_predict(feats: np.ndarray, W: np.ndarray, b: np.ndarray, filter_k: int = 20, bs: int = 32):
    """Online T3A over `feats` (N, D) in the given order.
    W (C, D), b (C,) are the linear classifier. Returns predicted labels (N,)."""
    n_cls = W.shape[0]
    norm = lambda a: a / (np.linalg.norm(a, axis=1, keepdims=True) + 1e-8)
    sup_z = norm(W.copy())
    sup_y = np.arange(n_cls)
    sup_ent = np.zeros(n_cls)  # classifier weights are always kept
    preds = []
    for i in range(0, len(feats), bs):
        z = feats[i:i + bs]
        logits = z @ W.T + b
        p = _softmax(logits)
        yhat = p.argmax(1)
        ent = -(p * np.log(p + 1e-8)).sum(1)
        sup_z = np.vstack([sup_z, norm(z)])
        sup_y = np.concatenate([sup_y, yhat])
        sup_ent = np.concatenate([sup_ent, ent])
        # keep the filter_k lowest-entropy supports per class
        keep = []
        for c in range(n_cls):
            ic = np.where(sup_y == c)[0]
            keep.extend(ic[np.argsort(sup_ent[ic])[:filter_k]])
        keep = np.array(sorted(keep))
        sup_z, sup_y, sup_ent = sup_z[keep], sup_y[keep], sup_ent[keep]
        protos = np.stack([sup_z[sup_y == c].mean(0) for c in range(n_cls)])
        preds.append((norm(z) @ norm(protos).T).argmax(1))
    return np.concatenate(preds)
