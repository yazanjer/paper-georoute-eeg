"""Rebuild curves/curves.json from the seed-0 re-run results (jobs 300, 301, 303, 305-309; run with --save-preds 1)."""
import glob, json, os
import numpy as np
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "results")
GROUPS = {"bnc_cbramod": ["300"], "bnc_eegnet": ["301"], "lee_cbramod": ["303", "305", "306"], "lee_eegnet": ["307", "308", "309"]}
ONL = ["source", "t3a", "lame", "tent", "tent@1e-4", "rctta", "rctta+t3a"]   # online methods (offline ones have no trajectory)
out = {}
for g, jobs in GROUPS.items():
    files = sorted(f for j in jobs for f in glob.glob(os.path.join(R, f"{j}_*", "*.json")))
    hist, blocks, accs = {}, {m: [] for m in ONL}, {}
    for f in files:
        r = json.load(open(f))
        if "preds" not in r:
            continue
        y, bs = np.array(r["y_stream"]), r["bs"]
        hist.setdefault(str(r["fold"]), [[round(a, 3), round(b, 3)] for a, b in r["train_hist"]])
        for m in ONL:
            c = (np.array(r["preds"][m]) == y).astype(float)
            blocks[m].append([c[i:i + bs].mean() for i in range(0, len(c), bs)])
        a = {m: round(v["acc"], 4) for m, v in r["methods"].items()}
        a["train_time_s"] = round(r["train_time_s"], 1)
        a.update({"t_" + k: round(v, 1) for k, v in r["time_s"].items()})
        accs[str(r["target"])] = a
    L = min(len(b) for b in blocks["source"])
    out[g] = {"n": len(accs), "bs": bs, "n_warmup": r["n_warmup"], "n_stream": len(y), "hist": hist,
              "blocks": {m: np.round(np.mean([b[:L] for b in v], 0), 4).tolist() for m, v in blocks.items()}, "accs": accs}
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "curves.json"), "w"), separators=(",", ":"))
print({g: (v["n"], len(v["hist"])) for g, v in out.items()})
