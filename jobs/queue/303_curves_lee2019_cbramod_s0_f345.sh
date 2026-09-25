#!/usr/bin/env bash
# CONVERGENCE RE-RUN (seed 0, frozen settings, geo_src omitted): Lee2019 CBraMod folds 3-5. Logs source training history and per-trial predictions.
# worker: R
set -e
cd "$(dirname "$0")/../.."
bash scripts/setup_env.sh
python scripts/run_tta.py --dataset lee2019_mi --backbone cbramod --seed 0 --cv kfold:6 --fold-ids 3,4,5 --methods source,t3a,lame,tent,tent@1e-4,shot_im,shot_im@1e-5,rctta,rctta+t3a,rctta_offline --save-preds 1 --ckpt-dir /workspace/ckpt_s0log --out "$RESULTS_DIR"
