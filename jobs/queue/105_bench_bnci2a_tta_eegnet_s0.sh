#!/usr/bin/env bash
# BENCHMARK (frozen protocol, see docs/BENCHMARK_PROTOCOL.md)
# worker: A
set -e
cd "$(dirname "$0")/../.."
bash scripts/setup_env.sh
python scripts/run_tta.py --dataset bnci2014_001 --seed 0 --cv loso --backbone eegnet --methods bench --out "$RESULTS_DIR"
