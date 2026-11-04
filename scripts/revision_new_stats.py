"""Statistics for the experiments added in review (jobs 400-491): sample-causal stream, warm-up length / cold start,
SHOT-IM adapted on the warm-up only, matched full fine-tuning of CBraMod, subject-level source validation, timing.

All numbers are computed from the unrounded per-run JSON files; output: paper/revision/new_stats.json
Run: python scripts/revision_new_stats.py
"""
from __future__ import annotations

import collections, glob, json, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from revision_stats import boot_mean_ci, wil, wtl, holm, RES, OUT  # noqa: E402

COND = ["c1", "bs1", "bs1w0", "bs1w32", "bs1w96", "valsubj_c1"]


def model_of(j):
    v = j["config"].get("variant", "-")
    vs = j["config"].get("val_by_subject", 0)
    m = "eegnet" if j["backbone"] == "eegnet" else ("fullft" if v == "fullft" else "lora")
    return ("valsubj_" + m) if vs else m


def load():
    acc = collections.defaultdict(dict)       # (ds, model, cond, method) -> {(subj, seed): acc}
    preds = collections.defaultdict(dict)     # (ds, model, cond) -> {(subj, seed): (y, {method: pred}, n_warmup)}
    fits = collections.defaultdict(list)
    seen = set()   # a pod that ran several jobs pushes its whole output dir, so files can appear in two job dirs
    for f in sorted(glob.glob(os.path.join(RES, "4[0-4]?_rev_*", "*_tta_*.json"))):
        if os.path.basename(f) in seen:
            continue
        seen.add(os.path.basename(f))
        j = json.load(open(f))
        cond = j["config"]["tag"].replace("_" + j["backbone"] + "_", "", 1)
        ds = "bci" if j["dataset"].startswith("bnci") else "lee"
        mdl = model_of(j)
        if cond.startswith("fullft_"):
            cond = cond[len("fullft_"):]
        key = (int(j["target"]), int(j["seed"]))
        for m, v in j["methods"].items():
            acc[(ds, mdl, cond, m)][key] = float(v["acc"])
        if "preds" in j:
            preds[(ds, mdl, cond)][key] = (j["y_stream"], j["preds"], j["n_warmup"])
        if j["config"].get("fit"):
            fits[(ds, mdl)].append(j["config"]["fit"])
    return acc, preds, fits


def subj_means(d, seeds=None):
    subs = sorted({s for s, _ in d})
    return subs, np.array([np.mean([v for (s, k), v in d.items() if s == q and (seeds is None or k in seeds)]) for q in subs])


def paired(da, db):
    """seed-matched paired difference (a - b) of subject means, in pp."""
    keys = sorted(set(da) & set(db))
    subs = sorted({s for s, _ in keys})
    d = np.array([100 * np.mean([da[k] - db[k] for k in keys if k[0] == s]) for s in subs])
    return {"n_subjects": len(subs), "seeds": sorted({k for _, k in keys}), "diff": float(d.mean()),
            "ci": boot_mean_ci(d), "W/T/L": wtl(d), "p": wil(d)}


def summary(acc, ds, mdl, cond, m):
    d = acc.get((ds, mdl, cond, m))
    if not d:
        return None
    subs, mu = subj_means(d)
    return {"mean": 100 * float(mu.mean()), "sd": 100 * float(mu.std(ddof=1)), "n_subjects": len(subs),
            "seeds": sorted({k for _, k in d}), "n_runs": len(d)}


def cold_curve(preds, ds, mdl, cond, methods, step):
    """Accuracy over the first k scored trials (k = step, 2 step, ...), mean over subject x seed runs."""
    out = {}
    runs = preds.get((ds, mdl, cond), {})
    if not runs:
        return None
    for m in methods:
        curves = []
        for (y, P, nw) in runs.values():
            if m not in P:
                continue
            c = (np.array(P[m][nw:]) == np.array(y[nw:])).astype(float)
            curves.append(np.cumsum(c) / np.arange(1, len(c) + 1))
        if curves:
            L = min(len(c) for c in curves)
            out[m] = {"k": list(range(step, L + 1, step)),
                      "acc": [100 * float(np.mean([c[k - 1] for c in curves])) for k in range(step, L + 1, step)]}
    return out


def timing():
    out = {}
    for job, ds in (("490_rev_timing_bnci2a", "bci"), ("491_rev_timing_lee", "lee")):
        for f in glob.glob(os.path.join(RES, job, "*_tta_*_timing.json")):
            j = json.load(open(f)); t = j.get("timing")
            if not t:
                continue
            e = out.setdefault(f"{ds}_{j['backbone']}", {"gpu": t["gpu"], "cpu": t["cpu"], "n_params_total": j["config"]["n_params_total"],
                                                         "n_params_trainable": j["config"]["n_params_trainable"],
                                                         "train_time_s": [], "methods": collections.defaultdict(lambda: {"total_s": [], "per_batch_ms": [], "mem": []})})
            e["train_time_s"].append(j["train_time_s"])
            for m, v in t["methods"].items():
                mm = e["methods"][m]
                mm["total_s"] += v["total_s"]; mm["mem"].append(v["peak_gpu_mem_mb"])
                if v["per_batch_ms"]:
                    mm["per_batch_ms"] += v["per_batch_ms"]
    res = {}
    for k, e in out.items():
        r = {kk: vv for kk, vv in e.items() if kk != "methods"}
        r["train_time_s"] = float(np.median(e["train_time_s"])) if e["train_time_s"] else None
        r["methods"] = {}
        for m, v in e["methods"].items():
            q = lambda a: [float(np.percentile(a, 25)), float(np.median(a)), float(np.percentile(a, 75))] if a else None
            r["methods"][m] = {"total_s_q": q(v["total_s"]), "per_batch_ms_q": q(v["per_batch_ms"]),
                               "peak_mem_mb": float(max(v["mem"])) if v["mem"] else None, "n": len(v["total_s"])}
        res[k] = r
    return res


def main():
    acc, preds, fits = load()
    R = {"summary": {}, "contrasts": {}, "cold": {}, "fits": {}}
    methods = ["source", "t3a", "lame", "tent", "tent@1e-4", "shot_im", "shot_im@1e-5", "shot_past", "shot_past@1e-5"]
    for ds in ("bci", "lee"):
        for mdl in ("lora", "eegnet", "fullft", "valsubj_lora", "valsubj_eegnet"):
            for cond in COND:
                for m in methods:
                    s = summary(acc, ds, mdl, cond, m)
                    if s:
                        R["summary"][f"{ds}|{mdl}|{cond}|{m}"] = s
    C = R["contrasts"]
    for ds in ("bci", "lee"):
        for mdl in ("lora", "eegnet", "fullft"):
            for cond in ("c1", "bs1", "bs1w0", "bs1w32", "bs1w96"):
                src = acc.get((ds, mdl, cond, "source"))
                if not src:
                    continue
                for m in ("t3a", "lame", "tent", "tent@1e-4", "shot_past", "shot_past@1e-5", "shot_im", "shot_im@1e-5"):
                    if (ds, mdl, cond, m) in acc:
                        C[f"{ds}|{mdl}|{cond}|{m}-source"] = paired(acc[(ds, mdl, cond, m)], src)
            # batch-causal vs sample-causal for the same method
            for m in ("source", "t3a", "tent", "tent@1e-4", "shot_past", "shot_past@1e-5"):
                if (ds, mdl, "bs1", m) in acc and (ds, mdl, "c1", m) in acc:
                    C[f"{ds}|{mdl}|bs1-c1|{m}"] = paired(acc[(ds, mdl, "bs1", m)], acc[(ds, mdl, "c1", m)])
            # transductive SHOT-IM vs warm-up-only SHOT-IM (same lr)
            for lr in ("", "@1e-5"):
                if (ds, mdl, "c1", "shot_im" + lr) in acc and (ds, mdl, "c1", "shot_past" + lr) in acc:
                    C[f"{ds}|{mdl}|c1|shot_im{lr}-shot_past{lr}"] = paired(acc[(ds, mdl, "c1", "shot_im" + lr)], acc[(ds, mdl, "c1", "shot_past" + lr)])
            # warm-up length effect relative to the full warm-up, sample-causal
            for w in ("bs1w0", "bs1w32", "bs1w96"):
                for m in ("source", "t3a", "tent@1e-4", "tent", "shot_past", "shot_past@1e-5"):
                    if (ds, mdl, w, m) in acc and (ds, mdl, "bs1", m) in acc:
                        C[f"{ds}|{mdl}|{w}-bs1|{m}"] = paired(acc[(ds, mdl, w, m)], acc[(ds, mdl, "bs1", m)])
        # backbones: EEGNet vs CBraMod-LoRA, and full FT vs LoRA, same condition and method
        for cond in ("c1", "bs1", "bs1w0", "bs1w32", "bs1w96"):
            for m in methods:
                a, b, f_ = (acc.get((ds, "eegnet", cond, m)), acc.get((ds, "lora", cond, m)), acc.get((ds, "fullft", cond, m)))
                if a and b:
                    C[f"{ds}|{cond}|{m}|eegnet-lora"] = paired(a, b)
                if f_ and b:
                    C[f"{ds}|{cond}|{m}|fullft-lora"] = paired(f_, b)
                if f_ and a:
                    C[f"{ds}|{cond}|{m}|eegnet-fullft"] = paired(a, f_)
        # subject-level vs trial-level source validation (same seeds)
        for mdl in ("lora", "eegnet"):
            for m in methods:
                a, b = acc.get((ds, "valsubj_" + mdl, "valsubj_c1", m)), acc.get((ds, mdl, "c1", m))
                if a and b:
                    C[f"{ds}|{mdl}|valsubj-trialval|{m}"] = paired(a, b)
        # cold-start curves
        for mdl in ("lora", "eegnet"):
            for cond in ("bs1w0", "bs1"):
                cc = cold_curve(preds, ds, mdl, cond, ["source", "t3a", "tent@1e-4", "tent"], 8 if ds == "bci" else 4)
                if cc:
                    R["cold"][f"{ds}|{mdl}|{cond}"] = cc
        for mdl in ("lora", "eegnet", "fullft", "valsubj_lora", "valsubj_eegnet"):
            F = fits.get((ds, mdl))
            if F:
                ep = [f["epochs_run"] for f in F]
                R["fits"][f"{ds}|{mdl}"] = {"epochs_median": float(np.median(ep)), "epochs_range": [int(min(ep)), int(max(ep))],
                                            "n_train": F[0]["n_train"], "n_val": F[0]["n_val"], "n": len(F)}
    R["timing"] = timing()
    # replication: re-run c1 source vs the original benchmark (same subject, seed)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import revision_stats as RS
    orig = RS.load_tta()
    rep = {}
    for ds in ("bci", "lee"):
        for mdl, bb in (("lora", "cbramod"), ("eegnet", "eegnet")):
            for m in ("source", "t3a", "shot_im", "shot_im@1e-5"):
                a, b = acc.get((ds, mdl, "c1", m)), orig.get((ds, bb, m))
                if a and b:
                    rep[f"{ds}|{mdl}|{m}"] = paired(a, b)
    R["replication_rerun_minus_original"] = rep
    json.dump(R, open(os.path.join(OUT, "new_stats.json"), "w"), indent=1)
    print("written", os.path.join(OUT, "new_stats.json"), len(R["summary"]), "cells")


if __name__ == "__main__":
    main()
