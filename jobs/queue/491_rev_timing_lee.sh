#!/usr/bin/env bash
# REVISION (IJIES 20267270): compute timing on one pod: Lee2019-MI seed 0, fold 0 (first 3 targets), both backbones, CUDA-synchronised, 3 repeats
# worker: L6
set -e
cd "$(dirname "$0")/../.."
export OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 NUMEXPR_NUM_THREADS=8
bash scripts/setup_env.sh
for B in cbramod eegnet; do python scripts/run_tta.py --dataset lee2019_mi --cv kfold:6 --seed 0 --fold-ids 0 --max-targets 3 --backbone $B --bs 32 --tag _timing --methods source,t3a,lame,tent,tent@1e-4,shot_im,shot_im@1e-5,shot_past,rctta,rctta+t3a,rctta_offline,geo_src --timing 1 --timing-repeats 3 --ckpt-dir /workspace/ckpt_rev --out "$RESULTS_DIR"; done
