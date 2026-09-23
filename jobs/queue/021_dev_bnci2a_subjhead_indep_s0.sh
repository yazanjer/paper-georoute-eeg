#!/usr/bin/env bash
# DEV: fully independent subject experts (no global adapter) with own heads, routed output ensemble.
set -e
cd "$(dirname "$0")/../.."
bash scripts/setup_env.sh
python scripts/run_georoute.py --dataset bnci2014_001 --seed 0 --cv loso --subject-head 1 --stage2 independent \
  --epochs-subject 30 --n-route 10,all --tag _shind --out "$RESULTS_DIR"
python scripts/aggregate.py --inputs "results/0[12][01]_*" --out "$RESULTS_DIR/summary"
