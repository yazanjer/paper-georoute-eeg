#!/usr/bin/env bash
# BENCHMARK (frozen protocol, see docs/BENCHMARK_PROTOCOL.md)
# worker: B
set -e
cd "$(dirname "$0")/../.."
bash scripts/setup_env.sh
python scripts/run_tta.py --dataset lee2019_mi --seed 0 --cv kfold:6 --backbone cbramod --methods bench --out "$RESULTS_DIR"
