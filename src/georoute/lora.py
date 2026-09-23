"""Multi-adapter LoRA for nn.Linear with exact weighted merging.

Each LoRALinear holds
  * a global adapter  (A_g, B_g)           -- shared across subjects
  * a bank of K subject adapters (A_k, B_k) -- one per source subject
and computes
  y = W x + b + s * [ B_g A_g x  +  sum_k w_k B_k A_k x ]
where the mixing weights w (K,) are set by the router (no gradients needed).
"""
from __future__ import annotations

import math
import torch
import torch.nn as nn


class LoRALinear(nn.Module):
    def __init__(self, base: nn.Linear, rank: int = 8, alpha: float = 16.0, dropout: float = 0.0):
        super().__init__()
        self.base = base
        for p in self.base.parameters():
            p.requires_grad = False
        self.rank, self.scale = rank, alpha / rank
        self.drop = nn.Dropout(dropout)
        fin, fout = base.in_features, base.out_features
        self.A_g = nn.Parameter(torch.empty(rank, fin))
        self.B_g = nn.Parameter(torch.zeros(fout, rank))
        nn.init.kaiming_uniform_(self.A_g, a=math.sqrt(5))
        self.bank_A = nn.ParameterList()
        self.bank_B = nn.ParameterList()
        self.register_buffer("mix", torch.zeros(0))
        self.use_global = True
        self.active: int | None = None  # train a single bank adapter

    # ---- bank management -------------------------------------------------
    def add_subject_adapter(self):
        fin, fout = self.base.in_features, self.base.out_features
        A = nn.Parameter(torch.empty(self.rank, fin, device=self.A_g.device))
        nn.init.kaiming_uniform_(A, a=math.sqrt(5))
        B = nn.Parameter(torch.zeros(fout, self.rank, device=self.A_g.device))
        self.bank_A.append(A)
        self.bank_B.append(B)
        return len(self.bank_A) - 1

    def forward(self, x):
        y = self.base(x)
        h = self.drop(x)
        if self.use_global:
            y = y + self.scale * (h @ self.A_g.t() @ self.B_g.t())
        if self.active is not None:
            k = self.active
            y = y + self.scale * (h @ self.bank_A[k].t() @ self.bank_B[k].t())
        elif self.mix.numel() > 0 and len(self.bank_A) > 0:
            for k in torch.nonzero(self.mix > 0).flatten().tolist():
                y = y + self.scale * self.mix[k] * (h @ self.bank_A[k].t() @ self.bank_B[k].t())
        return y


def inject_lora(model: nn.Module, target_names=("linear1", "linear2", "proj_out.0"),
                rank=8, alpha=16.0, dropout=0.0):
    """Replace matching nn.Linear submodules with LoRALinear. Returns list of wrappers."""
    wrappers = []
    for name, mod in list(model.named_modules()):
        for child_name, child in list(mod.named_children()):
            full = f"{name}.{child_name}" if name else child_name
            if isinstance(child, nn.Linear) and any(full.endswith(t) for t in target_names):
                w = LoRALinear(child, rank, alpha, dropout)
                setattr(mod, child_name, w)
                wrappers.append(w)
    return wrappers


def set_mode(wrappers, *, use_global=True, active=None, mix=None):
    for w in wrappers:
        w.use_global = use_global
        w.active = active
        if mix is not None:
            w.mix = torch.as_tensor(mix, dtype=torch.float32, device=w.A_g.device)
        elif active is not None:
            w.mix = torch.zeros(0, device=w.A_g.device)


def global_params(wrappers):
    return [p for w in wrappers for p in (w.A_g, w.B_g)]


def bank_params(wrappers, k):
    return [p for w in wrappers for p in (w.bank_A[k], w.bank_B[k])]
