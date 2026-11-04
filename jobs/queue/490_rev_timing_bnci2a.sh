#!/usr/bin/env bash
# REVISION (IJIES 20267270): compute timing on one pod: BCI IV-2a seed 0, folds 0-2, both backbones, CUDA-synchronised, 3 repeats
# worker: B1
set -e
cd "$(dirname "$0")/../.."
export OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 NUMEXPR_NUM_THREADS=8
bash scripts/setup_env.sh
for B in cbramod eegnet; do python scripts/run_tta.py --dataset bnci2014_001 --cv loso --seed 0 --fold-ids 0,1,2 --backbone $B --bs 32 --tag _timing --methods source,t3a,lame,tent,tent@1e-4,shot_im,shot_im@1e-5,shot_past,rctta,rctta+t3a,rctta_offline,geo_src --timing 1 --timing-repeats 3 --ckpt-dir /workspace/ckpt_rev --out "$RESULTS_DIR"; done
