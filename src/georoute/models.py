"""Foundation-model classifier (CBraMod backbone) and compact baselines."""
from __future__ import annotations

import warnings
import torch.nn as nn

CBRAMOD_HUB = "braindecode/cbramod-pretrained"


def load_cbramod(pretrained: bool = True):
    from braindecode.models import CBraMod
    if pretrained:
        m = CBraMod.from_pretrained(CBRAMOD_HUB, return_encoder_output=True)
        m.final_layer = nn.Identity()
        return m, True
    warnings.warn("CBraMod initialised RANDOMLY (no pretrained weights)")
    return CBraMod(n_outputs=2, n_chans=22, n_times=800, return_encoder_output=True), False


class FMClassifier(nn.Module):
    """Backbone -> mean over patches -> flatten channels -> MLP head."""

    def __init__(self, backbone: nn.Module, n_chans: int, n_classes: int,
                 emb_dim: int = 200, hidden: int = 256, drop: float = 0.3):
        super().__init__()
        self.backbone = backbone
        self.pre = nn.Sequential(nn.Flatten(), nn.Dropout(drop),
                                 nn.Linear(n_chans * emb_dim, hidden), nn.ELU(), nn.Dropout(drop))
        self.fc = nn.Linear(hidden, n_classes)

    def embed(self, x):
        f = self.backbone(x)          # (B, C, P, D)
        f = f.mean(dim=2)             # (B, C, D)
        return self.pre(f)            # (B, hidden)

    def forward(self, x):
        return self.fc(self.embed(x))

    def head_params(self):
        return list(self.pre.parameters()) + list(self.fc.parameters())


def compact_model(name: str, n_chans: int, n_classes: int, n_times: int):
    from braindecode.models import EEGNet, ShallowFBCSPNet, EEGConformer
    if name == "eegnet":
        return EEGNet(n_chans=n_chans, n_outputs=n_classes, n_times=n_times)
    if name == "shallow":
        return ShallowFBCSPNet(n_chans=n_chans, n_outputs=n_classes, n_times=n_times,
                               final_conv_length="auto")
    if name == "conformer":
        return EEGConformer(n_chans=n_chans, n_outputs=n_classes, n_times=n_times, sfreq=200)
    raise ValueError(name)
