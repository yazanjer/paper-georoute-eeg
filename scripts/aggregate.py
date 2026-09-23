"""Aggregate per-subject JSONs -> summary tables + paired statistics.

Output (in --out):
  per_subject.csv   dataset, seed, target, method, acc, bacc, kappa
  summary.csv       dataset, method, mean/sd over subjects (seed-averaged), sd over seeds, n
  stats.csv         Wilcoxon signed-rank (GeoRoute vs each method, per-subject seed-averaged acc),
                    Holm-corrected p, mean diff, rank-biserial effect size, wins/ties/losses
  routing.csv       per-subject Spearman(distance, single-adapter transfer)
  summary.md        markdown tables
"""
from __future__ import annotations

import argparse
import glob
import json
import os

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon


def holm(p):
    p = np.asarray(p, float)
    order = np.argsort(p)
    adj = np.empty_like(p)
    running = 0.0
    for i, j in enumerate(order):
        running = max(running, (len(p) - i) * p[j])
        adj[j] = min(1.0, running)
    return adj


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", default="results/*/")
    ap.add_argument("--ref", default="georoute")
    ap.add_argument("--out", default="results/summary")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rows, rrows = [], []
    for f in glob.glob(os.path.join(a.inputs, "*.json")):
        r = json.load(open(f))
        if "methods" not in r:
            continue
        for m, v in r["methods"].items():
            if "#" in m or "acc" not in v:
                continue
            rows.append(dict(dataset=r["dataset"], seed=r["seed"], target=r["target"], method=m,
                             acc=v["acc"], bacc=v.get("bacc"), kappa=v.get("kappa")))
        ro = r.get("routing", {})
        for key in ("spearman_riemann", "spearman_logeuclid", "spearman_euclid", "spearman_feature"):
            if key in ro:
                rrows.append(dict(dataset=r["dataset"], seed=r["seed"], target=r["target"],
                                  space=key.split("_", 1)[1], rho=ro[key][0], p=ro[key][1]))
    df = pd.DataFrame(rows).drop_duplicates(["dataset", "seed", "target", "method"], keep="last")
    df.to_csv(os.path.join(a.out, "per_subject.csv"), index=False)

    summ, stats = [], []
    for ds, g in df.groupby("dataset"):
        subj = g.groupby(["method", "target"])[["acc", "kappa"]].mean().reset_index()
        seed_means = g.groupby(["method", "seed"])["acc"].mean().reset_index()
        for m, gm in subj.groupby("method"):
            sd_seed = seed_means[seed_means.method == m]["acc"].std(ddof=1)
            summ.append(dict(dataset=ds, method=m, acc_mean=gm.acc.mean(), acc_sd_subjects=gm.acc.std(ddof=1),
                             acc_sd_seeds=sd_seed, kappa_mean=gm.kappa.mean(),
                             n_subjects=len(gm), n_seeds=int(seed_means[seed_means.method == m].seed.nunique())))
        ref = subj[subj.method == a.ref].set_index("target")["acc"]
        tmp = []
        for m, gm in subj.groupby("method"):
            if m == a.ref:
                continue
            x = gm.set_index("target")["acc"]
            common = ref.index.intersection(x.index)
            if len(common) < 5:
                continue
            d = ref[common].values - x[common].values
            nz = d[d != 0]
            p = wilcoxon(nz).pvalue if len(nz) > 0 else 1.0
            rpos = np.sum(d > 0); rneg = np.sum(d < 0)
            ranks = pd.Series(np.abs(nz)).rank().values
            rbc = (ranks[nz > 0].sum() - ranks[nz < 0].sum()) / ranks.sum() if len(nz) else 0.0
            tmp.append(dict(dataset=ds, ref=a.ref, vs=m, mean_diff=d.mean(), p=p, rank_biserial=rbc,
                            wins=int(rpos), ties=int(np.sum(d == 0)), losses=int(rneg), n=len(common)))
        if tmp:
            ph = holm([t["p"] for t in tmp])
            for t, pa in zip(tmp, ph):
                t["p_holm"] = pa
            stats.extend(tmp)
    S = pd.DataFrame(summ).sort_values(["dataset", "acc_mean"], ascending=[True, False])
    S.to_csv(os.path.join(a.out, "summary.csv"), index=False)
    P = pd.DataFrame(stats)
    P.to_csv(os.path.join(a.out, "stats.csv"), index=False)
    R = pd.DataFrame(rrows)
    R.to_csv(os.path.join(a.out, "routing.csv"), index=False)
    with open(os.path.join(a.out, "summary.md"), "w") as f:
        f.write("# Summary\n\n")
        f.write(S.to_markdown(index=False, floatfmt=".4f") + "\n\n")
        if len(P):
            f.write("## Paired tests vs %s\n\n" % a.ref + P.to_markdown(index=False, floatfmt=".4f") + "\n\n")
        if len(R):
            f.write("## Distance -> transfer Spearman (mean over subjects/seeds)\n\n")
            f.write(R.groupby(["dataset", "space"])["rho"].agg(["mean", "std", "count"]).to_markdown(floatfmt=".3f"))
    print(open(os.path.join(a.out, "summary.md")).read())


if __name__ == "__main__":
    main()
