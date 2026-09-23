#!/usr/bin/env bash
# Download Lee2019-MI (54 subjects, 2 sessions, 62 ch) via MOABB and build the 200 Hz cache.
set -e
cd "$(dirname "$0")/../.."
bash scripts/setup_env.sh
df -h /workspace | tail -1
python - <<'PY'
import json, os, sys, time
sys.path.insert(0, "src")
from georoute import data as D
t0 = time.time()
data, classes = D.load("lee2019_mi")
info = {"n_subjects": len(data), "classes": [str(c) for c in classes],
        "shape_sub1": list(data[sorted(data)[0]]["X"].shape),
        "trials_per_subject": {int(s): int(len(d["y"])) for s, d in data.items()},
        "sessions_sub1": sorted(set(data[sorted(data)[0]]["session"].tolist())),
        "x_std_sub1": float(data[sorted(data)[0]]["X"].std()),
        "minutes": round((time.time() - t0) / 60, 1)}
print(info)
json.dump(info, open(os.path.join(os.environ["RESULTS_DIR"], "lee2019_info.json"), "w"), indent=1)
PY
df -h /workspace | tail -1
du -sh /workspace/mne_data /workspace/cache || true
