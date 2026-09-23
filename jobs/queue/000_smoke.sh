#!/usr/bin/env bash
# Smoke test: GPU, env setup, pretrained CBraMod download, one MOABB subject, tiny GeoRoute run.
set -e
cd "$(dirname "$0")/../.."
nvidia-smi
bash scripts/setup_env.sh
python - <<'PY'
import json, os, sys, torch, moabb, braindecode, pyriemann
sys.path.insert(0, "src")
from georoute.models import load_cbramod
m, pre = load_cbramod(True)
x = torch.randn(2, 22, 800)
out = m(x)
info = dict(torch=torch.__version__, cuda=torch.cuda.is_available(),
            gpu=torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
            braindecode=braindecode.__version__, moabb=moabb.__version__, pyriemann=pyriemann.__version__,
            cbramod_pretrained=pre, cbramod_out_shape=list(out.shape))
from georoute import data as D
d, cls = D.load("bnci2014_001", subjects=[1])
info["bnci_sub1"] = dict(X=list(d[1]["X"].shape), classes=[str(c) for c in cls],
                         sessions=sorted(set(d[1]["session"].tolist())),
                         x_std=float(d[1]["X"].std()))
print(info)
json.dump(info, open(os.path.join(os.environ["RESULTS_DIR"], "env.json"), "w"), indent=2)
PY
python scripts/run_georoute.py --synthetic 1 --pretrained 1 --epochs-global 2 --epochs-subject 1 --fold-ids 0 --n-route all --out "$RESULTS_DIR/synthetic"
