"""Training / evaluation utilities."""
from __future__ import annotations

import random
import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import accuracy_score, balanced_accuracy_score, cohen_kappa_score

DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def seed_all(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def _batches(n, bs, rng, shuffle=True):
    idx = rng.permutation(n) if shuffle else np.arange(n)
    for i in range(0, n, bs):
        yield idx[i:i + bs]


def fit(model: nn.Module, params, X, y, *, epochs=30, lr=1e-3, wd=1e-2, bs=64,
        val_frac=0.1, seed=0, param_groups=None, patience=8, label_smoothing=0.1):
    """Train `params` (others frozen by caller) with a random val split and
    early stopping on val loss. Restores the best state. Returns history dict."""
    rng = np.random.default_rng(seed)
    n = len(y)
    idx = rng.permutation(n)
    n_val = max(int(n * val_frac), 1) if val_frac > 0 else 0
    va, tr = idx[:n_val], idx[n_val:]
    model.to(DEV)
    opt = torch.optim.AdamW(param_groups or [{"params": params, "lr": lr}], lr=lr, weight_decay=wd)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(epochs, 1))
    crit = nn.CrossEntropyLoss(label_smoothing=label_smoothing)
    best, best_state, bad, hist = np.inf, None, 0, []
    Xt, yt = torch.from_numpy(X), torch.from_numpy(y)
    for ep in range(epochs):
        model.train()
        tl = 0.0
        for b in _batches(len(tr), bs, rng):
            bi = tr[b]
            xb, yb = Xt[bi].to(DEV), yt[bi].to(DEV)
            loss = crit(model(xb), yb)
            opt.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_([p for g in opt.param_groups for p in g["params"]], 5.0)
            opt.step()
            tl += loss.item() * len(bi)
        sched.step()
        if n_val:
            vl = evaluate_loss(model, X[va], y[va], crit)
            hist.append((tl / len(tr), vl))
            if vl < best - 1e-4:
                best, bad = vl, 0
                best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
            else:
                bad += 1
                if bad >= patience:
                    break
    if best_state is not None:
        model.load_state_dict(best_state)
    return {"epochs_run": len(hist), "best_val_loss": float(best), "hist": hist}


@torch.no_grad()
def evaluate_loss(model, X, y, crit):
    model.eval()
    tot = 0.0
    for i in range(0, len(y), 256):
        xb = torch.from_numpy(X[i:i + 256]).to(DEV)
        yb = torch.from_numpy(y[i:i + 256]).to(DEV)
        tot += crit(model(xb), yb).item() * len(yb)
    return tot / len(y)


@torch.no_grad()
def predict_logits(model, X, bs=256):
    model.eval().to(DEV)
    out = [model(torch.from_numpy(X[i:i + bs]).to(DEV)).float().cpu() for i in range(0, len(X), bs)]
    return torch.cat(out).numpy()


@torch.no_grad()
def embed(model, X, bs=256):
    model.eval().to(DEV)
    out = [model.embed(torch.from_numpy(X[i:i + bs]).to(DEV)).float().cpu() for i in range(0, len(X), bs)]
    return torch.cat(out).numpy()


def metrics(y_true, y_pred):
    return {"acc": float(accuracy_score(y_true, y_pred)),
            "bacc": float(balanced_accuracy_score(y_true, y_pred)),
            "kappa": float(cohen_kappa_score(y_true, y_pred))}
