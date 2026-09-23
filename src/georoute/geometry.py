"""Covariance geometry: Euclidean alignment and subject-level distances."""
from __future__ import annotations

import numpy as np
from scipy.linalg import sqrtm, inv
from pyriemann.estimation import Covariances
from pyriemann.utils.mean import mean_riemann, mean_logeuclid
from pyriemann.utils.distance import distance_riemann, distance_logeuclid


def covs(X: np.ndarray) -> np.ndarray:
    return Covariances(estimator="oas").fit_transform(X.astype(np.float64))


def ea_matrix(X: np.ndarray) -> np.ndarray:
    """Euclidean alignment: R^{-1/2} with R the arithmetic mean covariance."""
    R = covs(X).mean(0)
    return np.real(inv(sqrtm(R))).astype(np.float32)


def apply_ea(X: np.ndarray, W: np.ndarray) -> np.ndarray:
    return np.einsum("ij,njt->nit", W, X).astype(np.float32)


def subject_mean(X: np.ndarray, metric: str = "riemann") -> np.ndarray:
    C = covs(X)
    if metric == "riemann":
        return mean_riemann(C)
    if metric == "logeuclid":
        return mean_logeuclid(C)
    return C.mean(0)  # euclid


def distance(A: np.ndarray, B: np.ndarray, metric: str = "riemann") -> float:
    if metric == "riemann":
        return float(distance_riemann(A, B))
    if metric == "logeuclid":
        return float(distance_logeuclid(A, B))
    return float(np.linalg.norm(A - B, "fro"))


def routing_weights(dists: np.ndarray, top_k: int | None, tau: float | str = "auto") -> np.ndarray:
    """softmax(-d/tau) over the top-k nearest source subjects, zeros elsewhere.

    tau="auto" uses the median of the selected distances, making the weights
    scale-free across datasets and metrics (no tuning on target data).
    """
    d = np.asarray(dists, dtype=np.float64)
    k = len(d) if not top_k or top_k >= len(d) else top_k
    idx = np.argsort(d)[:k]
    t = float(np.median(d[idx])) if tau == "auto" else float(tau)
    t = max(t, 1e-8)
    z = -d[idx] / t
    z -= z.max()
    w_sel = np.exp(z) / np.exp(z).sum()
    w = np.zeros_like(d)
    w[idx] = w_sel
    return w
