#!/usr/bin/env bash
# REVISION (IJIES 20267270): smoke test of the revision code paths on synthetic data
# worker: B1
set -e
cd "$(dirname "$0")/../.."
export OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 NUMEXPR_NUM_THREADS=8
bash scripts/setup_env.sh
for M in lora fullft eegnet valsubj_lora; do
  python scripts/run_tta.py --synthetic 1 --backbone $([ $M = eegnet ] && echo eegnet || echo cbramod) --variant $([ $M = fullft ] && echo fullft || echo lora) --val-by-subject $([ $M = valsubj_lora ] && echo 1 || echo 0) --epochs 2 --cv loso --fold-ids 0 --bs 1 --warmup 8 --tag _smoke_$M --methods source,t3a,tent@1e-4,shot_past,geo_src --timing 1 --timing-repeats 2 --save-preds 1 --ckpt-dir /workspace/ckpt_smoke --out "$RESULTS_DIR"
done
