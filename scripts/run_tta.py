"""Online test-time adaptation benchmark (cross-subject, calibration-free).

Protocol (identical for every method):
  * source model trained on the source subjects of the fold (EA per source subject)
  * target stream = session 1 (unscored warm-up) followed by the evaluation session,
    presented in fixed chronological order, batch size --bs
  * Euclidean alignment of the stream is ONLINE (running mean of past+current trials)
  * online methods predict-then-update; nothing ever sees target labels
  * only the evaluation session is scored

Methods
  source        no adaptation
  t3a           T3A prototype adjustment (backprop-free)
  lame          LAME output adaptation (backprop-free)
  tent          Tent: entropy minimisation on normalisation affine params (backprop)
  shot_im       SHOT-IM, offline on the whole unlabeled stream (backprop, upper-ish baseline)
  rctta         ours
  rctta+t3a     ours with T3A posteriors as the decoder evidence
  rctta_* ablations: lam0.5 / lam2 / nobp (no 8-30 Hz band) / norecenter / nogate (n0=0)
  rctta_offline ours, transductive over the whole stream
  geo_src       source-trained Riemannian MDM with online re-centring (geometry alone)
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import sys
import time

import numpy as np
import torch
import torch.nn as nn

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from georoute import data as D, geometry as G, lora as L, train as T, rctta as R  # noqa: E402
from georoute.models import load_cbramod, FMClassifier, compact_model  # noqa: E402
sys.path.insert(0, os.path.dirname(__file__))
from run_georoute import folds  # noqa: E402

ALL = ("source,t3a,lame,tent,shot_im,rctta,rctta+t3a,rctta_lam0.5,rctta_lam2,rctta_nobp,"
       "rctta_norecenter,rctta_nogate,rctta_offline,geo_src")


# ------------------------------------------------------------------ decoders
class Decoder:
    """Uniform interface: logits + penultimate features + last linear layer (W, b)."""

    def __init__(self, kind, model):
        self.kind, self.model = kind, model
        if kind == "eegnet":
            self._feat = None
            conv = model.final_layer.conv_classifier
            conv.register_forward_hook(lambda m, i, o: setattr(self, "_feat", i[0]))

    @torch.no_grad()
    def forward(self, X, bs=256):
        self.model.eval().to(T.DEV)
        L_, F_ = [], []
        for i in range(0, len(X), bs):
            xb = torch.from_numpy(np.ascontiguousarray(X[i:i + bs], dtype=np.float32)).to(T.DEV)
            if self.kind == "cbramod":
                f = self.model.embed(xb)
                z = self.model.fc(f)
            else:
                z = self.model(xb)
                f = self._feat.flatten(1)
            L_.append(z.float().cpu()); F_.append(f.float().cpu())
        return torch.cat(L_).numpy(), torch.cat(F_).numpy()

    def linear(self):
        if self.kind == "cbramod":
            return (self.model.fc.weight.detach().cpu().numpy(), self.model.fc.bias.detach().cpu().numpy())
        c = self.model.final_layer.conv_classifier
        return (c.weight.detach().flatten(1).cpu().numpy(), c.bias.detach().cpu().numpy())

    def norm_params(self):
        ps = []
        for m in self.model.modules():
            if isinstance(m, (nn.LayerNorm, nn.GroupNorm, nn.BatchNorm1d, nn.BatchNorm2d)) and m.weight is not None:
                ps += [m.weight, m.bias]
        return ps


def train_source(kind, Xs, ys, C, n_cls, Tn, a, ckpt):
    if kind == "cbramod":
        bb, _ = load_cbramod(not a.synthetic)
        model = FMClassifier(bb, C, n_cls).to(T.DEV)
        wr = L.inject_lora(model.backbone, rank=a.rank)
        for w in wr:
            w.to(T.DEV)
        for p in model.backbone.parameters():
            p.requires_grad = False
        ps = L.global_params(wr) + model.head_params()
        for p in ps:
            p.requires_grad = True
    else:
        model = compact_model(kind, C, n_cls, Tn).to(T.DEV)
        ps = list(model.parameters())
    if os.path.exists(ckpt):
        model.load_state_dict(torch.load(ckpt, map_location=T.DEV))
        return model
    T.fit(model, ps, Xs, ys, epochs=a.epochs, lr=a.lr, bs=64, seed=a.seed,
          patience=8 if kind == "cbramod" else 15)
    os.makedirs(os.path.dirname(ckpt), exist_ok=True)
    torch.save(model.state_dict(), ckpt)
    return model


# ------------------------------------------------------------------ methods
def stream_batches(Xstream, bs):
    ea = R.OnlineEA()
    for i in range(0, len(Xstream), bs):
        yield i, ea(Xstream[i:i + bs])


def run_backpropfree(dec, Xstream, bs, n_cls, which):
    """All backprop-free methods in one pass over the stream (shared EA + forward)."""
    W, b = dec.linear()
    out = {m: [] for m in which}
    t3a_gen, t3a_q = None, []
    feats_all = []
    rc = {
        "rctta": R.RCTTA(n_cls), "rctta+t3a": R.RCTTA(n_cls),
        "rctta_lam0.5": R.RCTTA(n_cls, lam=0.5), "rctta_lam2": R.RCTTA(n_cls, lam=2.0),
        "rctta_nobp": R.RCTTA(n_cls, band=None), "rctta_norecenter": R.RCTTA(n_cls, recenter=False),
        "rctta_nogate": R.RCTTA(n_cls, n0=0), "rctta_offline": R.RCTTA(n_cls),
    }
    rc = {k: v for k, v in rc.items() if k in which}

    def t3a_feed():
        while True:
            yield feats_all[-1]
    t3a_gen = R.t3a_stream(t3a_feed(), W, b)
    for i, Xa in stream_batches(Xstream, bs):
        z, f = dec.forward(Xa)
        p = R.softmax(z)
        feats_all.append(f)
        pt = next(t3a_gen)
        if "source" in out: out["source"].append(p)
        if "t3a" in out: out["t3a"].append(pt)
        if "lame" in out: out["lame"].append(R.lame(p, f))
        for k, obj in rc.items():
            q = obj.step(Xa, pt if k == "rctta+t3a" else p)
            if k != "rctta_offline":
                out[k].append(q)
    res = {k: np.concatenate(v) for k, v in out.items() if v}
    if "rctta_offline" in rc:  # transductive: one EM pass over everything seen, final posteriors
        obj = rc["rctta_offline"]
        n = len(obj.C); lam_eff = obj.lam * n / (n + obj.n0)
        Tg = obj._tangent(); logpf = np.log(obj.P + 1e-8); q = obj.P.copy()
        for _ in range(obj.em_iters):
            w = q * q.max(1, keepdims=True)
            mu = (w.T @ Tg) / (w.sum(0)[:, None] + 1e-8)
            d2 = ((Tg[:, None, :] - mu[None]) ** 2).sum(-1)
            q = R.softmax(logpf + lam_eff * np.log(R.softmax(-d2 / (np.median(d2) + 1e-8)) + 1e-8))
        res["rctta_offline"] = q
    return res


def run_tent(dec, Xstream, bs, lr=1e-3):
    dec2 = Decoder(dec.kind, copy.deepcopy(dec.model))
    model = dec2.model.to(T.DEV)
    for p in model.parameters():
        p.requires_grad = False
    ps = dec2.norm_params()
    for p in ps:
        p.requires_grad = True
    opt = torch.optim.SGD(ps, lr=lr, momentum=0.9)
    outs = []
    for i, Xa in stream_batches(Xstream, bs):
        model.train()  # BN uses batch stats (Tent); dropout off below
        for m in model.modules():
            if isinstance(m, nn.Dropout):
                m.eval()
        xb = torch.from_numpy(np.ascontiguousarray(Xa)).to(T.DEV)
        z = model.fc(model.embed(xb)) if dec.kind == "cbramod" else model(xb)
        p = torch.softmax(z, 1)
        outs.append(p.detach().cpu().numpy())
        loss = -(p * torch.log(p + 1e-8)).sum(1).mean()
        opt.zero_grad(); loss.backward(); opt.step()
    return np.concatenate(outs)


def run_shot_im(dec, Xstream, bs, epochs=10, lr=1e-4):
    """Offline SHOT-IM: maximise information (low entropy, high diversity); last layer frozen."""
    dec2 = Decoder(dec.kind, copy.deepcopy(dec.model))
    model = dec2.model.to(T.DEV)
    # align the whole stream once with the online EA (last reference = full stream)
    Xa = np.concatenate([x for _, x in stream_batches(Xstream, bs)])
    last = model.fc if dec.kind == "cbramod" else model.final_layer.conv_classifier
    for p in model.parameters():
        p.requires_grad = True
    for p in last.parameters():
        p.requires_grad = False
    ps = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.Adam(ps, lr=lr)
    Xt = torch.from_numpy(np.ascontiguousarray(Xa))
    rng = np.random.default_rng(0)
    for _ in range(epochs):
        model.train()
        for idx in np.array_split(rng.permutation(len(Xt)), max(1, len(Xt) // 32)):
            xb = Xt[idx].to(T.DEV)
            z = model.fc(model.embed(xb)) if dec.kind == "cbramod" else model(xb)
            p = torch.softmax(z, 1)
            ent = -(p * torch.log(p + 1e-8)).sum(1).mean()
            pm = p.mean(0)
            div = (pm * torch.log(pm + 1e-8)).sum()
            loss = ent + div
            opt.zero_grad(); loss.backward(); opt.step()
    z, _ = dec2.forward(Xa)
    return R.softmax(z)


def run_geo_src(data, sources, Xstream, bs, n_cls):
    """Source-trained MDM on re-centred 8-30 Hz covariances; target re-centred online."""
    from pyriemann.classification import MDM
    from pyriemann.utils.mean import mean_riemann
    from scipy.linalg import fractional_matrix_power as fmp

    def rc(C, ref):
        M = np.real(fmp(ref, -0.5))
        return np.einsum("ij,njk,kl->nil", M, C, M)
    Cs, ys = [], []
    for s in sources:
        C = R.covs(R.bandpass(data[s]["X"]))
        Cs.append(rc(C, mean_riemann(C))); ys.append(data[s]["y"])
    clf = MDM().fit(np.concatenate(Cs), np.concatenate(ys))
    outs, seen = [], None
    for i in range(0, len(Xstream), bs):
        Cb = R.covs(R.bandpass(Xstream[i:i + bs]))
        seen = Cb if seen is None else np.concatenate([seen, Cb])
        outs.append(clf.predict_proba(rc(Cb, mean_riemann(seen))))
    return np.concatenate(outs)


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="bnci2014_001")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--cv", default="loso")
    ap.add_argument("--fold-ids", default="all")
    ap.add_argument("--backbone", default="cbramod", choices=["cbramod", "eegnet"])
    ap.add_argument("--methods", default=ALL)
    ap.add_argument("--bs", type=int, default=32)
    ap.add_argument("--epochs", type=int, default=0, help="0 = backbone default (30 FM / 100 EEGNet)")
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--rank", type=int, default=8)
    ap.add_argument("--synthetic", type=int, default=0)
    ap.add_argument("--ckpt-dir", default=os.environ.get("GEOROUTE_CKPT", "/workspace/ckpt"))
    ap.add_argument("--out", default=os.environ.get("RESULTS_DIR", "results/local"))
    a = ap.parse_args()
    a.epochs = a.epochs or (30 if a.backbone == "cbramod" else 100)
    os.makedirs(a.out, exist_ok=True)
    which = a.methods.split(",")

    data, classes = D.synthetic() if a.synthetic else D.load(a.dataset)
    subjects = sorted(data)
    n_cls = len(classes)
    C, Tn = data[subjects[0]]["X"].shape[1:]
    fl = folds(subjects, a.cv, a.seed)
    fold_ids = range(len(fl)) if a.fold_ids == "all" else [int(i) for i in a.fold_ids.split(",")]
    ea_W = {s: G.ea_matrix(data[s]["X"]) for s in subjects}

    for fi in fold_ids:
        targets = fl[fi]
        sources = [s for s in subjects if s not in targets]
        T.seed_all(a.seed * 1000 + fi)
        Xs = np.concatenate([G.apply_ea(data[s]["X"], ea_W[s]) for s in sources])
        ys = np.concatenate([data[s]["y"] for s in sources])
        tag = "synthetic" if a.synthetic else a.dataset
        ckpt = os.path.join(a.ckpt_dir, f"{tag}_{a.backbone}_s{a.seed}_{a.cv.replace(':', '')}_f{fi}.pt")
        t0 = time.time()
        model = train_source(a.backbone, Xs, ys, C, n_cls, Tn, a, ckpt)
        dec = Decoder(a.backbone, model)
        t_train = time.time() - t0
        for t in targets:
            d = data[t]
            r_idx, e_idx = D.split_target(d)
            order = np.concatenate([r_idx, e_idx])      # warm-up session, then scored session
            Xstream, ystream = d["X"][order], d["y"][order]
            scored = np.arange(len(r_idx), len(order))
            res = {"dataset": a.dataset, "seed": a.seed, "fold": fi, "target": int(t),
                   "backbone": a.backbone, "bs": a.bs, "n_warmup": int(len(r_idx)),
                   "n_scored": int(len(e_idx)), "train_time_s": t_train, "methods": {},
                   "config": {"tag": f"_{a.backbone}"}, "time_s": {}}
            probs = {}
            t1 = time.time()
            bpf = [m for m in which if m in ("source", "t3a", "lame") or m.startswith("rctta")]
            if bpf:
                probs.update(run_backpropfree(dec, Xstream, a.bs, n_cls, bpf))
                res["time_s"]["backprop_free_all"] = time.time() - t1
            if "tent" in which:
                t1 = time.time(); probs["tent"] = run_tent(dec, Xstream, a.bs); res["time_s"]["tent"] = time.time() - t1
            if "shot_im" in which:
                t1 = time.time(); probs["shot_im"] = run_shot_im(dec, Xstream, a.bs); res["time_s"]["shot_im"] = time.time() - t1
            if "geo_src" in which:
                t1 = time.time(); probs["geo_src"] = run_geo_src(data, sources, Xstream, a.bs, n_cls)
                res["time_s"]["geo_src"] = time.time() - t1
            for m, P in probs.items():
                res["methods"][m] = T.metrics(ystream[scored], P[scored].argmax(1))
            fn = os.path.join(a.out, f"{a.dataset}_seed{a.seed}_sub{int(t):03d}_tta_{a.backbone}.json")
            json.dump(res, open(fn, "w"), indent=1)
            mm = res["methods"]
            print(f"[fold {fi}] target {t} ({a.backbone}): " + " ".join(
                f"{k}={mm[k]['acc']:.3f}" for k in ("source", "t3a", "lame", "tent", "rctta", "rctta+t3a") if k in mm),
                flush=True)
        del model, dec
        torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
