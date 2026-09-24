#!/usr/bin/env bash
# BENCHMARK (frozen protocol, see docs/BENCHMARK_PROTOCOL.md)
# worker: D
set -e
cd "$(dirname "$0")/../.."
bash scripts/setup_env.sh
python scripts/run_baselines.py --dataset bnci2014_001 --seed 1 --cv loso --out "$RESULTS_DIR"
