"""Dataset loading via MOABB with an on-disk cache.

Every dataset is returned as a dict  subject -> dict(X, y, session)  with
X in microvolts / 100 (CBraMod convention), float32, shape (n, C, T) at 200 Hz.
The evaluation split used everywhere:
    * routing / alignment trials  = target subject's FIRST session (labels unused)
    * evaluation trials           = target subject's LAST session
so the unlabeled trials used for routing never overlap the evaluation trials.
"""
from __future__ import annotations

import os
import numpy as np

SFREQ = 200
CACHE_VERSION = "v2"  # v2: unit auto-detection (uV vs V)
CACHE = os.environ.get("GEOROUTE_CACHE", "/workspace/cache")
if os.path.isdir("/workspace"):  # keep MOABB downloads on the persistent pod volume
    os.environ.setdefault("MNE_DATA", "/workspace/mne_data")
    os.makedirs(os.environ["MNE_DATA"], exist_ok=True)

DATASETS = {
    # name: (moabb class, n_classes, tmin, tmax, events)
    "bnci2014_001": ("BNCI2014_001", 4, 0.0, 4.0, None),
    "lee2019_mi": ("Lee2019_MI", 2, 0.0, 4.0, None),
    "physionet_mi": ("PhysionetMI", 4, 0.0, 3.0, None),
}


def _load_moabb(name: str, subjects=None):
    import moabb.datasets as mds
    from moabb.paradigms import MotorImagery

    cls_name, n_classes, tmin, tmax, events = DATASETS[name]
    ds = getattr(mds, cls_name)()
    subs = subjects or ds.subject_list
    paradigm = MotorImagery(n_classes=n_classes, fmin=0.5, fmax=45.0,
                            tmin=tmin, tmax=tmax, resample=SFREQ, events=events)
    out = {}
    for s in subs:
        X, labels, meta = paradigm.get_data(dataset=ds, subjects=[s])
        classes = sorted(np.unique(labels))
        y = np.array([classes.index(l) for l in labels], dtype=np.int64)
        X = X.astype(np.float64)
        # MOABB returns volts for most sources but some (e.g. BNCI via the newer
        # NeMAR mirror) arrive in microvolts: detect by magnitude.
        if np.median(X.std(axis=-1)) < 1e-2:
            X = X * 1e6                      # V -> uV
        X = (X / 100.0).astype(np.float32)   # uV / 100 (CBraMod convention)
        n_t = int(round((tmax - tmin) * SFREQ))
        X = X[..., :n_t]
        out[s] = dict(X=X, y=y, session=np.asarray(meta["session"].astype(str)))
    return out, classes


def load(name: str, subjects=None):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, f"{name}_{CACHE_VERSION}.npz")
    if os.path.exists(path) and subjects is None:
        z = np.load(path, allow_pickle=True)
        return z["data"].item(), list(z["classes"])
    data, classes = _load_moabb(name, subjects)
    if subjects is None:
        np.savez(path, data=np.array(data, dtype=object), classes=np.array(classes))
    return data, classes


def split_target(d: dict):
    """Return (routing_idx, eval_idx) for a target subject."""
    sess = d["session"]
    uniq = sorted(np.unique(sess))
    if len(uniq) >= 2:
        return np.where(sess == uniq[0])[0], np.where(sess == uniq[-1])[0]
    # single-session datasets: first 50% of trials (chronological) route, rest eval
    n = len(sess)
    return np.arange(n // 2), np.arange(n // 2, n)


def synthetic(n_subjects=5, n_trials=80, n_chans=22, n_times=800, n_classes=4, seed=0):
    """Tiny synthetic dataset for CPU unit tests."""
    rng = np.random.default_rng(seed)
    data = {}
    for s in range(1, n_subjects + 1):
        mix = rng.normal(size=(n_chans, n_chans)) * (0.5 + s * 0.1)
        y = rng.integers(0, n_classes, n_trials)
        X = rng.normal(size=(n_trials, n_chans, n_times)).astype(np.float32)
        X[np.arange(n_trials), y % n_chans] *= 3
        X = np.einsum("ij,njt->nit", mix, X).astype(np.float32) * 0.2
        sess = np.array(["0train"] * (n_trials // 2) + ["1test"] * (n_trials - n_trials // 2))
        data[s] = dict(X=X, y=y.astype(np.int64), session=sess)
    return data, list(range(n_classes))
