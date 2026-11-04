"""Revision statistics (IJIES review, Nov 2026), computed from the committed per-subject result files.

Everything is recomputed from UNROUNDED per-(subject, seed) accuracies; rounding to one decimal happens only
when a number is printed (round-half-to-even on the unrounded value, Python's format()).

Outputs (to paper/revision/):
  unrounded_tta.csv          per dataset/backbone/method/subject/seed accuracy (fraction) + seed means
  summary_tta.json           mean, SD, delta vs source, W/T/L (ties explicit), runs below source, Holm p,
                             paired bootstrap CI of the delta, failure rate with subject-cluster bootstrap CI,
                             loss distribution and meaningful-deterioration rates
  online_vs_offline.json     best strictly-online method per backbone vs offline SHOT-IM (paired diff + CI)
  hypotheses.json            H1-H4 with paired effects, 95 % bootstrap CIs and a single Holm family
  geometry_margins.json      GeoRoute / RCTTA contrasts with CIs against the 1.0 pp (pilot) and 1.5 pp (H4) margins
Run:  python scripts/revision_stats.py
"""
from __future__ import annotations

import collections
import glob
import json
import os

import numpy as np
from scipy.stats import wilcoxon

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RES = os.path.join(ROOT, "results")
OUT = os.path.join(ROOT, "paper", "revision")
B = 10000            # bootstrap resamples (subjects)
RNG = np.random.default_rng(20261104)

ONLINE = ["t3a", "lame", "tent", "tent@1e-4", "rctta", "rctta+t3a", "geo_src"]   # batch-causal online methods
OFFLINE = ["shot_im", "shot_im@1e-5", "rctta_offline"]                             # transductive over the stream
METHODS = ["source"] + ONLINE[:-1] + OFFLINE[:2] + ["rctta_offline"]
NAMES = {"source": "Source", "t3a": "T3A", "lame": "LAME", "tent": "Tent 1e-3", "tent@1e-4": "Tent 1e-4",
         "shot_im": "SHOT-IM 1e-4 (offline)", "shot_im@1e-5": "SHOT-IM 1e-5 (offline)", "rctta": "RCTTA",
         "rctta+t3a": "RCTTA+T3A", "rctta_offline": "RCTTA offline (transductive)", "geo_src": "MDM-RC"}


def holm(ps):
    ps = np.asarray(ps, float)
    o = np.argsort(ps)
    adj = np.empty_like(ps)
    run = 0.0
    for k, i in enumerate(o):
        run = max(run, min(1.0, (len(ps) - k) * ps[i]))
        adj[i] = run
    return adj


def wil(d):
    d = np.asarray(d, float)
    if np.allclose(d, 0):
        return 1.0
    return float(wilcoxon(d, zero_method="wilcox", alternative="two-sided").pvalue)


def boot_mean_ci(d, b=B):
    d = np.asarray(d, float)
    idx = RNG.integers(0, len(d), size=(b, len(d)))
    m = d[idx].mean(1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def wtl(d, tol=1e-9):
    d = np.asarray(d, float)
    return int((d > tol).sum()), int((np.abs(d) <= tol).sum()), int((d < -tol).sum())


# ------------------------------------------------------------------ load benchmark TTA results
def load_tta():
    acc = collections.defaultdict(dict)   # (ds, bb, method) -> {(subject, seed): acc}
    for f in glob.glob(os.path.join(RES, "1[0-3]?_bench_*", "*_tta_*.json")):
        j = json.load(open(f))
        ds = "bci" if j["dataset"].startswith("bnci") else "lee"
        for m, v in j["methods"].items():
            acc[(ds, j["backbone"], m)][(int(j["target"]), int(j["seed"]))] = float(v["acc"])
    return acc


def matrix(acc, ds, bb, m):
    """subjects x seeds array (NaN where missing)."""
    d = acc[(ds, bb, m)]
    subs = sorted({s for s, _ in d})
    seeds = sorted({k for _, k in d})
    A = np.full((len(subs), len(seeds)), np.nan)
    for i, s in enumerate(subs):
        for j, k in enumerate(seeds):
            A[i, j] = d.get((s, k), np.nan)
    return subs, seeds, A


def cluster_boot_rate(below, b=B):
    """below: subjects x seeds boolean. Resample subjects (clusters), keep all their seeds."""
    n = below.shape[0]
    idx = RNG.integers(0, n, size=(b, n))
    r = below[idx].mean(axis=(1, 2))
    return [float(np.percentile(r, 2.5)), float(np.percentile(r, 97.5))]


def summarise_tta(acc):
    rows, summ = [], {}
    for ds in ("bci", "lee"):
        for bb in ("cbramod", "eegnet"):
            subs, seeds, S = matrix(acc, ds, bb, "source")
            src = S.mean(1)
            cell = {}
            ps = {}
            for m in METHODS + ["geo_src"]:
                if (ds, bb, m) not in acc:
                    continue
                s2, k2, A = matrix(acc, ds, bb, m)
                assert s2 == subs
                for i, s in enumerate(subs):
                    for j, k in enumerate(k2):
                        if not np.isnan(A[i, j]):
                            rows.append((ds, bb, m, s, k, A[i, j]))
                mean_s = np.nanmean(A, 1)
                e = {"n_subjects": len(subs), "seeds": k2, "mean": 100 * float(mean_s.mean()),
                     "sd_subjects": 100 * float(mean_s.std(ddof=1)),
                     "seed_sd_of_mean": 100 * float(np.nanmean(A, 0).std(ddof=1)) if len(k2) > 1 else None}
                if m != "source" and m != "geo_src":
                    d = 100 * (mean_s - src)
                    w, t, l = wtl(d)
                    common = [j for j, k in enumerate(seeds) if k in k2]
                    below = (A[:, :len(common)] < S[:, common] - 1e-12)
                    loss = 100 * (S[:, common] - A[:, :len(common)])          # positive = worse than source
                    runs_loss = loss[loss > 1e-12]
                    e.update({
                        "delta": float(d.mean()), "delta_ci": boot_mean_ci(d), "W": w, "T": t, "L": l,
                        "runs": int(below.size), "runs_below": int(below.sum()),
                        "runs_tied": int((np.abs(loss) <= 1e-12).sum()),
                        "failure_rate": float(below.mean()), "failure_rate_ci": cluster_boot_rate(below),
                        "runs_loss_ge5pp": int((loss >= 5 - 1e-9).sum()), "runs_loss_ge10pp": int((loss >= 10 - 1e-9).sum()),
                        "loss_quantiles_pp_given_below": ([float(np.percentile(runs_loss, q)) for q in (25, 50, 75, 90)]
                                                          if len(runs_loss) else None),
                        "worst_run_loss_pp": float(loss.max()),
                    })
                    ps[m] = wil(d)
                cell[m] = e
            if ps:
                adj = holm(list(ps.values()))
                for (m, p), a in zip(ps.items(), adj):
                    cell[m]["p_raw"], cell[m]["p_holm"] = p, float(a)
            summ[f"{ds}_{bb}"] = cell
    return rows, summ


def online_vs_offline(acc, summ):
    out = {}
    for ds in ("bci", "lee"):
        for bb in ("cbramod", "eegnet"):
            cell = summ[f"{ds}_{bb}"]
            best_on = max([m for m in ONLINE if m in cell and m != "geo_src"], key=lambda m: cell[m]["mean"])
            best_off = max([m for m in OFFLINE[:2] if m in cell], key=lambda m: cell[m]["mean"])
            _, _, A = matrix(acc, ds, bb, best_on)
            _, _, Bm = matrix(acc, ds, bb, best_off)
            d = 100 * (np.nanmean(Bm, 1) - np.nanmean(A, 1))
            out[f"{ds}_{bb}"] = {"best_online": best_on, "best_online_mean": cell[best_on]["mean"],
                                 "best_offline": best_off, "best_offline_mean": cell[best_off]["mean"],
                                 "offline_minus_online": float(d.mean()), "ci": boot_mean_ci(d),
                                 "W/T/L": wtl(d), "p": wil(d)}
    # cross-backbone: best strictly-online EEGNet vs best strictly-online CBraMod
    for ds in ("bci", "lee"):
        a, b = out[f"{ds}_eegnet"]["best_online"], out[f"{ds}_cbramod"]["best_online"]
        _, _, A = matrix(acc, ds, "eegnet", a)
        _, _, Bm = matrix(acc, ds, "cbramod", b)
        d = 100 * (np.nanmean(A, 1) - np.nanmean(Bm, 1))
        out[f"{ds}_online_eegnet_minus_cbramod"] = {"eegnet": a, "cbramod": b, "diff": float(d.mean()),
                                                   "ci": boot_mean_ci(d), "W/T/L": wtl(d), "p": wil(d)}
    return out


# ------------------------------------------------------------------ GeoRoute contrasts
def load_geo():
    acc = collections.defaultdict(dict)
    for job in ("010_pilot_bnci2a_georoute_s0", "110_bench_bnci2a_georoute_s1", "111_bench_bnci2a_georoute_s2",
                "031_confirm_lee2019_georoute_s0"):
        for f in glob.glob(os.path.join(RES, job, "*.json")):
            j = json.load(open(f))
            if "methods" not in j:
                continue
            ds = "bci" if j["dataset"].startswith("bnci") else "lee"
            for m, v in j["methods"].items():
                if isinstance(v, dict) and "acc" in v:
                    acc[(ds, m)][(int(j["target"]), int(j["seed"]))] = float(v["acc"])
    return acc


def geo_contrast(gacc, ds, a, b):
    da, db = gacc[(ds, a)], gacc[(ds, b)]
    keys = sorted(set(da) & set(db))
    subs = sorted({s for s, _ in keys})
    d = np.array([100 * np.mean([da[k] - db[k] for k in keys if k[0] == s]) for s in subs])
    return {"a": a, "b": b, "n_subjects": len(subs), "seeds": sorted({k for _, k in keys}),
            "diff": float(d.mean()), "ci": boot_mean_ci(d), "W/T/L": wtl(d), "p": wil(d)}


def main():
    os.makedirs(OUT, exist_ok=True)
    acc = load_tta()
    rows, summ = summarise_tta(acc)
    with open(os.path.join(OUT, "unrounded_tta.csv"), "w") as f:
        f.write("dataset,backbone,method,subject,seed,acc\n")
        for r in sorted(rows):
            f.write(",".join(map(str, r[:5])) + f",{r[5]:.10f}\n")
    json.dump(summ, open(os.path.join(OUT, "summary_tta.json"), "w"), indent=1)
    ovo = online_vs_offline(acc, summ)
    json.dump(ovo, open(os.path.join(OUT, "online_vs_offline.json"), "w"), indent=1)

    # ---- hypotheses: one confirmatory family (H1, H2 on both datasets = 4 Wilcoxon tests), Holm across it
    hyp = {}
    tests = []
    for ds in ("bci", "lee"):
        _, _, Se = matrix(acc, ds, "eegnet", "source")
        _, _, Sc = matrix(acc, ds, "cbramod", "source")
        d1 = 100 * (Se.mean(1) - Sc.mean(1))
        _, _, T = matrix(acc, ds, "cbramod", "t3a")
        d2 = 100 * (T.mean(1) - Sc.mean(1))
        for h, d in (("H1", d1), ("H2", d2)):
            e = {"diff": float(d.mean()), "ci": boot_mean_ci(d), "W/T/L": wtl(d), "p_raw": wil(d)}
            hyp[f"{h}_{ds}"] = e
            tests.append(f"{h}_{ds}")
    adj = holm([hyp[t]["p_raw"] for t in tests])
    for t, a in zip(tests, adj):
        hyp[t]["p_holm_family4"] = float(a)
    # H3: failure counts compared descriptively (difference of failure rates with subject-cluster bootstrap)
    for ds in ("bci", "lee"):
        for m in ("tent", "shot_im"):
            out = {}
            for bb in ("cbramod", "eegnet"):
                _, _, S = matrix(acc, ds, bb, "source")
                _, _, A = matrix(acc, ds, bb, m)
                out[bb] = (A < S - 1e-12)
            dd = out["cbramod"].mean() - out["eegnet"].mean()
            n = out["cbramod"].shape[0]
            idx = RNG.integers(0, n, size=(B, n))
            bs = out["cbramod"][idx].mean(axis=(1, 2)) - out["eegnet"][idx].mean(axis=(1, 2))
            hyp[f"H3_{ds}_{m}"] = {"rate_cbramod": float(out["cbramod"].mean()), "rate_eegnet": float(out["eegnet"].mean()),
                                   "diff": float(dd), "ci": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]}
    json.dump(hyp, open(os.path.join(OUT, "hypotheses.json"), "w"), indent=1)

    # ---- geometry margins
    gacc = load_geo()
    geo = {}
    for ds in ("bci", "lee"):
        for a, b in (("georoute", "shared_only"), ("georoute_ens", "uniform_ens"), ("georoute_ens", "random_ens"),
                     ("georoute+t3a", "shared_only+t3a"), ("oracle_best_single", "uniform_ens")):
            if (ds, a) in gacc and (ds, b) in gacc:
                geo[f"{ds}:{a}-{b}"] = geo_contrast(gacc, ds, a, b)
        for bb in ("cbramod", "eegnet"):
            _, _, T = matrix(acc, ds, bb, "t3a")
            _, _, RT = matrix(acc, ds, bb, "rctta+t3a")
            d = 100 * (RT.mean(1) - T.mean(1))
            geo[f"{ds}:{bb}:rctta+t3a-t3a"] = {"diff": float(d.mean()), "ci": boot_mean_ci(d), "W/T/L": wtl(d), "p": wil(d)}
    for k, v in geo.items():
        v["excludes_gain_ge_1.5pp"] = bool(v["ci"][1] < 1.5)
        v["excludes_gain_ge_1.0pp"] = bool(v["ci"][1] < 1.0)
    json.dump(geo, open(os.path.join(OUT, "geometry_margins.json"), "w"), indent=1)
    print("written to", OUT)


if __name__ == "__main__":
    main()
