"""Rebuild agg.json (seed-averaged per-subject accuracy) from ../results/*/*.json."""
import collections, glob, json, os
import numpy as np
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
KEEP_GEO = ['shared_only', 'uniform_ens', 'random_ens', 'georoute_ens', 'georoute',
            'shared_only+t3a', 'georoute+t3a', 'oracle_best_single']
agg = collections.defaultdict(list)
for f in glob.glob(os.path.join(R, "*", "*.json")):
    job = os.path.basename(os.path.dirname(f))[:3]
    if job in ("040", "041", "000", "020", "021", "030", "200", "201") or job[0] == "3":   # 3xx = seed-0 re-run (curves)
        continue
    try:
        j = json.load(open(f))
    except Exception:
        continue
    if "methods" not in j or "dataset" not in j:
        continue
    if job in ("010", "110", "111"): grp = "geo_bci"
    elif job == "031": grp = "geo_lee"
    elif job in ("011", "140", "141"): grp = "base_bci"
    elif job in ("151", "152", "153"): grp = "base_lee"
    elif "backbone" in j: grp = f"tta_{j['dataset'][:3]}_{j['backbone']}"
    else: continue
    for m, v in j["methods"].items():
        if isinstance(v, dict) and "acc" in v:
            agg[(grp, m, int(j["target"]))].append(float(v["acc"]))
out = {}
for (grp, m, s), v in agg.items():
    out.setdefault(grp, {}).setdefault(m, {})[str(s)] = round(100 * float(np.mean(v)), 2)
for g in ("geo_bci", "geo_lee"):
    out[g] = {m: out[g][m] for m in KEEP_GEO if m in out.get(g, {})}
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "agg.json"), "w"), separators=(",", ":"))
print({g: len(v) for g, v in out.items()})
