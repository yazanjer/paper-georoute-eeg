#!/usr/bin/env bash
# CONVERGENCE RE-RUN (seed 0, frozen settings): Lee2019-MI eegnet, folds 4,5. Replaces the aborted job 304
# (its pod's CPU made the backprop-free methods ~50x slower). Thread caps only affect speed, not results.
# worker: X
set -e
cd "$(dirname "$0")/../.."
export OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 NUMEXPR_NUM_THREADS=8
bash scripts/setup_env.sh
python scripts/run_tta.py --dataset lee2019_mi --backbone eegnet --seed 0 --cv kfold:6 --fold-ids 4,5 --methods source,t3a,lame,tent,tent@1e-4,shot_im,shot_im@1e-5,rctta,rctta+t3a,rctta_offline --save-preds 1 --ckpt-dir /workspace/ckpt_s0log --out "$RESULTS_DIR"
