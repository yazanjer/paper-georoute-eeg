#!/usr/bin/env bash
# BENCHMARK (frozen protocol, see docs/BENCHMARK_PROTOCOL.md)
# worker: E
set -e
cd "$(dirname "$0")/../.."
bash scripts/setup_env.sh
python scripts/run_tta.py --dataset lee2019_mi --seed 1 --cv kfold:6 --backbone eegnet --methods bench --out "$RESULTS_DIR"
