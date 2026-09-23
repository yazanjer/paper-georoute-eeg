"""Cross-subject baselines under the exact GeoRoute protocol (same folds / splits).

methods:
  csp_lda[_ea]         classical: CSP (+EA) + LDA
  mdm_ra               Riemannian MDM with per-subject re-centering (RA)
  ts_lr_ra             tangent space + logistic regression with RA
  eegnet[_ea], shallow[_ea], conformer[_ea]   compact deep nets trained from scratch
  cbramod_fullft[_ea]  full fine-tuning of the pretrained foundation model
  cbramod_lp[_ea]      linear probe (frozen backbone, head only)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from georoute import data as D, geometry as G, train as T  # noqa: E402
from georoute.models import load_cbramod, FMClassifier, compact_model  # noqa: E402
sys.path.insert(0, os.path.dirname(__file__))
from run_georoute import folds  # noqa: E402


def classical(method, Xs_list, ys, Xt_route, Xt_eval):
    from pyriemann.estimation import Covariances
    from pyriemann.classification import MDM
    from pyriemann.tangentspace import TangentSpace
    from pyriemann.utils.mean import mean_riemann
    from pyriemann.spatialfilters import CSP
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from scipy.linalg import fractional_matrix_power as fmp

    cov = Covariances("oas")
    if method.startswith("csp_lda"):
        Cs = np.concatenate([cov.fit_transform(X.astype(np.float64)) for X in Xs_list])
        clf = make_pipeline(CSP(nfilter=8, log=True), LDA())
        clf.fit(Cs, ys)
        return clf.predict(cov.fit_transform(Xt_eval.astype(np.float64)))

    def recenter(Cx, Cref):  # Riemannian alignment (Zanini et al. 2018)
        M = np.real(fmp(mean_riemann(Cref), -0.5))
        return np.einsum("ij,njk,kl->nil", M, Cx, M)

    Cs = np.concatenate([recenter(c, c) for c in (cov.fit_transform(X.astype(np.float64)) for X in Xs_list)])
    Ct_r = cov.fit_transform(Xt_route.astype(np.float64))
    Ct_e = recenter(cov.fit_transform(Xt_eval.astype(np.float64)), Ct_r)
    clf = MDM() if method == "mdm_ra" else make_pipeline(TangentSpace(), LogisticRegression(max_iter=2000))
    clf.fit(Cs, ys)
    return clf.predict(Ct_e)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="bnci2014_001")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--cv", default="loso")
    ap.add_argument("--fold-ids", default="all")
    ap.add_argument("--methods", default="csp_lda_ea,mdm_ra,ts_lr_ra,eegnet,eegnet_ea,shallow_ea,conformer_ea,cbramod_lp_ea,cbramod_fullft_ea")
    ap.add_argument("--epochs", type=int, default=100)
    ap.add_argument("--epochs-fm", type=int, default=30)
    ap.add_argument("--synthetic", type=int, default=0)
    ap.add_argument("--pretrained", type=int, default=1)
    ap.add_argument("--out", default=os.environ.get("RESULTS_DIR", "results/local"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    data, classes = D.synthetic() if a.synthetic else D.load(a.dataset)
    subjects = sorted(data)
    n_cls = len(classes)
    C, Tn = data[subjects[0]]["X"].shape[1:]
    fl = folds(subjects, a.cv, a.seed)
    fold_ids = range(len(fl)) if a.fold_ids == "all" else [int(i) for i in a.fold_ids.split(",")]
    methods = a.methods.split(",")
    ea_W = {s: G.ea_matrix(data[s]["X"]) for s in subjects}

    for fi in fold_ids:
        targets = fl[fi]
        sources = [s for s in subjects if s not in targets]
        ys = np.concatenate([data[s]["y"] for s in sources])
        out = {t: {} for t in targets}
        for meth in methods:
            T.seed_all(a.seed * 1000 + fi)
            use_ea = meth.endswith("_ea")
            base = meth[:-3] if use_ea else meth
            Xs = [G.apply_ea(data[s]["X"], ea_W[s]) if use_ea else data[s]["X"] for s in sources]
            t0 = time.time()
            if base in ("csp_lda", "mdm_ra", "ts_lr_ra"):
                for t in targets:
                    r, e = D.split_target(data[t])
                    Xr, Xe = data[t]["X"][r], data[t]["X"][e]
                    if use_ea:
                        Xe = G.apply_ea(Xe, G.ea_matrix(Xr))
                    pred = classical(base, Xs, ys, Xr, Xe)
                    out[t][meth] = T.metrics(data[t]["y"][e], pred)
                continue
            if base in ("eegnet", "shallow", "conformer"):
                model = compact_model(base, C, n_cls, Tn)
                T.fit(model, list(model.parameters()), np.concatenate(Xs), ys,
                      epochs=a.epochs, lr=1e-3, bs=64, seed=a.seed, patience=15)
            elif base in ("cbramod_fullft", "cbramod_lp"):
                bb, _ = load_cbramod(bool(a.pretrained))
                model = FMClassifier(bb, C, n_cls).to(T.DEV)
                if base == "cbramod_lp":
                    for p in model.backbone.parameters():
                        p.requires_grad = False
                    groups = [{"params": model.head_params(), "lr": 1e-3}]
                else:
                    groups = [{"params": list(model.backbone.parameters()), "lr": 1e-4},
                              {"params": model.head_params(), "lr": 1e-3}]
                T.fit(model, None, np.concatenate(Xs), ys, epochs=a.epochs_fm, bs=64,
                      seed=a.seed, param_groups=groups)
            else:
                raise ValueError(meth)
            for t in targets:
                r, e = D.split_target(data[t])
                Xe = data[t]["X"][e]
                if use_ea:
                    Xe = G.apply_ea(Xe, G.ea_matrix(data[t]["X"][r]))
                out[t][meth] = T.metrics(data[t]["y"][e], T.predict_logits(model, Xe).argmax(1))
                out[t][meth]["train_time_s"] = time.time() - t0
            print(f"[fold {fi}] {meth}: " + " ".join(f"{t}:{out[t][meth]['acc']:.3f}" for t in targets), flush=True)
        for t in targets:
            fn = os.path.join(a.out, f"{a.dataset}_seed{a.seed}_sub{int(t):03d}_baselines.json")
            json.dump({"dataset": a.dataset, "seed": a.seed, "fold": fi, "target": int(t),
                       "methods": out[t]}, open(fn, "w"), indent=1)


if __name__ == "__main__":
    main()
