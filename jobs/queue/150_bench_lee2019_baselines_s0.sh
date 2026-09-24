#!/usr/bin/env bash
# BENCHMARK (frozen protocol, see docs/BENCHMARK_PROTOCOL.md)
# worker: E
set -e
cd "$(dirname "$0")/../.."
bash scripts/setup_env.sh
python scripts/run_baselines.py --dataset lee2019_mi --seed 0 --cv kfold:6 --methods csp_lda_ea,mdm_ra,ts_lr_ra,eegnet_ea,shallow_ea,cbramod_lp_ea,cbramod_fullft_ea --out "$RESULTS_DIR"
