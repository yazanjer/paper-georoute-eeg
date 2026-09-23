"""GeoRoute main experiment (cross-subject, calibration-free).

Per fold:
  1. Stage 1  - train a GLOBAL LoRA adapter + head on all source subjects.
  2. Stage 2  - train one SUBJECT LoRA adapter per source subject (global + head frozen).
  3. Target   - unlabeled first-session trials -> covariance mean -> distances to
                every source subject -> weighted merge of subject adapters.
All routing variants (metrics, top-k, N unlabeled trials, controls) share the
same trained bank, so ablations are free and exactly paired.

Writes one JSON per target subject to $RESULTS_DIR.
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import os
import sys
import time

import numpy as np
import torch
from scipy.stats import spearmanr

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from georoute import data as D, geometry as G, lora as L, train as T, tta  # noqa: E402
from georoute.models import load_cbramod, FMClassifier  # noqa: E402


def folds(subjects, cv, seed):
    subjects = list(subjects)
    if cv == "loso":
        return [[s] for s in subjects]
    k = int(cv.split(":")[1])
    rng = np.random.default_rng(1234)  # fixed across seeds -> paired comparisons
    perm = list(rng.permutation(subjects))
    return [sorted(perm[i::k]) for i in range(k)]


def prep(X, W):
    return G.apply_ea(X, W) if W is not None else X


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="bnci2014_001")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--cv", default="loso")
    ap.add_argument("--fold-ids", default="all", help="comma list of fold indices or 'all'")
    ap.add_argument("--ea", type=int, default=1)
    ap.add_argument("--rank", type=int, default=8)
    ap.add_argument("--epochs-global", type=int, default=30)
    ap.add_argument("--epochs-subject", type=int, default=20)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--bs", type=int, default=64)
    ap.add_argument("--n-route", default="5,10,20,50,all")
    ap.add_argument("--pretrained", type=int, default=1)
    ap.add_argument("--synthetic", type=int, default=0)
    ap.add_argument("--max-subjects", type=int, default=0)
    ap.add_argument("--stage2", default="residual", choices=["residual", "independent"],
                    help="residual: subject adapters on top of the global one; independent: global off")
    ap.add_argument("--subject-head", type=int, default=0,
                    help="1: each subject adapter also gets its own copy of the head")
    ap.add_argument("--tag", default="", help="suffix for output file names")
    ap.add_argument("--out", default=os.environ.get("RESULTS_DIR", "results/local"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    data, classes = D.synthetic() if a.synthetic else D.load(a.dataset)
    subjects = sorted(data)[: a.max_subjects or None]
    n_cls = len(classes)
    C, Tn = data[subjects[0]]["X"].shape[1:]
    fl = folds(subjects, a.cv, a.seed)
    fold_ids = range(len(fl)) if a.fold_ids == "all" else [int(i) for i in a.fold_ids.split(",")]

    # subject-level raw covariance means (pre-EA) for every subject, all trials
    means = {m: {} for m in ("riemann", "logeuclid", "euclid")}
    for s in subjects:
        for m in means:
            means[m][s] = G.subject_mean(data[s]["X"], m)
    ea_W = {s: (G.ea_matrix(data[s]["X"]) if a.ea else None) for s in subjects}

    for fi in fold_ids:
        targets = fl[fi]
        sources = [s for s in subjects if s not in targets]
        K = len(sources)
        t0 = time.time()
        T.seed_all(a.seed * 1000 + fi)

        # ---------------- Stage 1: global adapter + head ------------------
        backbone, is_pre = load_cbramod(bool(a.pretrained))
        model = FMClassifier(backbone, C, n_cls).to(T.DEV)
        wr = L.inject_lora(model.backbone, rank=a.rank)
        for w in wr:
            w.to(T.DEV)
        for p in model.backbone.parameters():
            p.requires_grad = False
        Xs = np.concatenate([prep(data[s]["X"], ea_W[s]) for s in sources])
        ys = np.concatenate([data[s]["y"] for s in sources])
        L.set_mode(wr, use_global=True, active=None, mix=np.zeros(0))
        gparams = L.global_params(wr) + model.head_params()
        for p in gparams:
            p.requires_grad = True
        h1 = T.fit(model, gparams, Xs, ys, epochs=a.epochs_global, lr=a.lr, bs=a.bs, seed=a.seed)

        # ---------------- Stage 2: subject adapters ----------------------
        for p in gparams:
            p.requires_grad = False
        use_g2 = a.stage2 == "residual"
        head_mods = [model.pre, model.fc]
        g_head = [copy.deepcopy(m.state_dict()) for m in head_mods]
        heads = []
        h2 = {}
        for k, s in enumerate(sources):
            for w in wr:
                w.add_subject_adapter()
            L.set_mode(wr, use_global=use_g2, active=k)
            bp = L.bank_params(wr, k)
            if a.subject_head:
                for m, st in zip(head_mods, g_head):
                    m.load_state_dict(st)
                bp = bp + model.head_params()
            for p in bp:
                p.requires_grad = True
            h2[int(s)] = T.fit(model, bp, prep(data[s]["X"], ea_W[s]), data[s]["y"],
                               epochs=a.epochs_subject, lr=a.lr, bs=a.bs, seed=a.seed + k)
            for p in bp:
                p.requires_grad = False
            heads.append([copy.deepcopy(m.state_dict()) for m in head_mods])
        for m, st in zip(head_mods, g_head):
            m.load_state_dict(st)
        train_time = time.time() - t0

        def expert_probs(Xe):
            """(K, N, C) softmax outputs of each subject expert (adapter [+ own head])."""
            out = []
            for k in range(K):
                L.set_mode(wr, use_global=use_g2, active=k)
                if a.subject_head:
                    for m, st in zip(head_mods, heads[k]):
                        m.load_state_dict(st)
                z = T.predict_logits(model, Xe)
                z = np.exp(z - z.max(1, keepdims=True))
                out.append(z / z.sum(1, keepdims=True))
            for m, st in zip(head_mods, g_head):
                m.load_state_dict(st)
            L.set_mode(wr, use_global=True, active=None, mix=np.zeros(K))
            return np.stack(out)

        # ---------------- Target evaluation -------------------------------
        topk_auto = max(1, math.ceil(math.sqrt(K)))
        for t in targets:
            d = data[t]
            r_idx, e_idx = D.split_target(d)
            y_e = d["y"][e_idx]
            res = {"dataset": a.dataset, "seed": a.seed, "fold": fi, "target": int(t),
                   "sources": [int(s) for s in sources], "K": K, "topk_auto": topk_auto,
                   "pretrained": is_pre, "ea": a.ea, "rank": a.rank,
                   "n_route_trials": int(len(r_idx)), "n_eval_trials": int(len(e_idx)),
                   "train_time_s": train_time, "stage1": {k: v for k, v in h1.items() if k != "hist"},
                   "methods": {}, "routing": {}}

            def ens(P, wts, tag):
                pred = np.tensordot(wts, P, axes=1).argmax(1)
                res["methods"][tag] = T.metrics(y_e, pred)
                return res["methods"][tag]

            def run(mix, tag, Xe, use_global=True, t3a=False):
                L.set_mode(wr, use_global=use_global, active=None, mix=mix)
                if t3a:
                    f = T.embed(model, Xe)
                    pred = tta.t3a_predict(f, model.fc.weight.detach().cpu().numpy(),
                                           model.fc.bias.detach().cpu().numpy())
                else:
                    pred = T.predict_logits(model, Xe).argmax(1)
                res["methods"][tag] = T.metrics(y_e, pred)
                return res["methods"][tag]

            n_routes = [len(r_idx) if n == "all" else min(int(n), len(r_idx))
                        for n in a.n_route.split(",")]
            n_full = len(r_idx)
            for n in sorted(set(n_routes)):
                ridx = r_idx[:n]
                W_t = G.ea_matrix(d["X"][ridx]) if a.ea else None
                Xe = prep(d["X"][e_idx], W_t)
                suf = "" if n == n_full else f"@n{n}"
                dists = {m: np.array([G.distance(G.subject_mean(d["X"][ridx], m), means[m][s], m)
                                      for s in sources]) for m in means}
                res["routing"][f"dist{suf}"] = {m: v.tolist() for m, v in dists.items()}
                wts = G.routing_weights(dists["riemann"], topk_auto)
                res["routing"][f"weights{suf}"] = wts.tolist()
                run(wts, f"georoute{suf}", Xe)
                P = expert_probs(Xe)
                ens(P, wts, f"georoute_ens{suf}")
                if n != n_full:
                    continue
                ens(P, np.full(K, 1.0 / K), "uniform_ens")
                for m in ("logeuclid", "euclid"):
                    ens(P, G.routing_weights(dists[m], topk_auto), f"georoute_ens[{m}]")
                for k in (1, 3, 5, 8, K):
                    if k <= K:
                        ens(P, G.routing_weights(dists["riemann"], k), f"georoute_ens[top{k}]")
                rng_e = np.random.default_rng(a.seed * 7919 + int(t) + 1)
                rnd_e = [ens(P, G.routing_weights(rng_e.permutation(dists["riemann"]), topk_auto),
                             f"random_ens#{i}")["acc"] for i in range(5)]
                res["methods"]["random_ens"] = {"acc": float(np.mean(rnd_e))}
                acc_e = [T.metrics(y_e, P[k].argmax(1))["acc"] for k in range(K)]
                res["routing"]["acc_single_expert"] = acc_e
                res["methods"]["oracle_best_expert"] = {"acc": float(max(acc_e))}
                for m in ("riemann", "logeuclid", "euclid"):
                    rho, pv = spearmanr(-dists[m], acc_e)
                    res["routing"][f"spearman_ens_{m}"] = [float(rho), float(pv)]
                # ---- everything below uses all routing trials -------------
                run(np.zeros(K), "shared_only", Xe)
                run(np.full(K, 1.0 / K), "uniform_merge", Xe)
                run(wts, "georoute+t3a", Xe, t3a=True)
                run(np.zeros(K), "shared_only+t3a", Xe, t3a=True)
                for m in ("logeuclid", "euclid"):
                    run(G.routing_weights(dists[m], topk_auto), f"georoute[{m}]", Xe)
                for k in (1, 3, 5, 8, K):
                    if k <= K:
                        run(G.routing_weights(dists["riemann"], k), f"georoute[top{k}]", Xe)
                rng = np.random.default_rng(a.seed * 7919 + int(t))
                rnd = [run(G.routing_weights(rng.permutation(dists["riemann"]), topk_auto),
                           f"random_route#{i}", Xe)["acc"] for i in range(5)]
                res["methods"]["random_route"] = {"acc": float(np.mean(rnd))}
                # feature-space routing: distance between mean shared-model embeddings
                L.set_mode(wr, use_global=True, active=None, mix=np.zeros(K))
                ft = T.embed(model, Xe).mean(0)
                fdist = np.array([np.linalg.norm(ft - T.embed(model, prep(data[s]["X"], ea_W[s])).mean(0))
                                  for s in sources])
                res["routing"]["dist_feature"] = fdist.tolist()
                run(G.routing_weights(fdist, topk_auto), "georoute[feature]", Xe)
                ens(P, G.routing_weights(fdist, topk_auto), "georoute_ens[feature]")
                # per-adapter transfer (analysis: does distance predict transfer?)
                acc_k = []
                for k in range(K):
                    e = np.zeros(K); e[k] = 1.0
                    L.set_mode(wr, use_global=True, active=None, mix=e)
                    acc_k.append(T.metrics(y_e, T.predict_logits(model, Xe).argmax(1))["acc"])
                res["routing"]["acc_single_adapter"] = acc_k
                for m in ("riemann", "logeuclid", "euclid"):
                    rho, pv = spearmanr(-dists[m], acc_k)
                    res["routing"][f"spearman_{m}"] = [float(rho), float(pv)]
                rho, pv = spearmanr(-fdist, acc_k)
                res["routing"]["spearman_feature"] = [float(rho), float(pv)]
                res["methods"]["oracle_best_single"] = {"acc": float(max(acc_k))}
            res["config"] = {"stage2": a.stage2, "subject_head": a.subject_head, "rank": a.rank,
                             "epochs_subject": a.epochs_subject, "tag": a.tag}
            fn = os.path.join(a.out, f"{a.dataset}_seed{a.seed}_sub{int(t):03d}{a.tag}.json")
            json.dump(res, open(fn, "w"), indent=1)
            m = res["methods"]
            print(f"[fold {fi}] target {t}: shared {m['shared_only']['acc']:.3f} "
                  f"uniform {m['uniform_merge']['acc']:.3f} georoute {m['georoute']['acc']:.3f} "
                  f"georoute_ens {m['georoute_ens']['acc']:.3f} uniform_ens {m['uniform_ens']['acc']:.3f} "
                  f"rho {res['routing']['spearman_riemann'][0]:.2f}", flush=True)
        del model, wr
        torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
