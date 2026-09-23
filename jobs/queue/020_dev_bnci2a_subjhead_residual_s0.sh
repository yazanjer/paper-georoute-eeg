#!/usr/bin/env bash
# DEV (after pilot no-go on parameter merging): subject adapters + own heads (residual on global),
# routed OUTPUT ensemble. BCI IV-2a LOSO seed 0.
set -e
cd "$(dirname "$0")/../.."
bash scripts/setup_env.sh
python scripts/run_georoute.py --dataset bnci2014_001 --seed 0 --cv loso --subject-head 1 --stage2 residual \
  --epochs-subject 30 --n-route 10,all --tag _shres --out "$RESULTS_DIR"
python scripts/aggregate.py --inputs "results/0[12][01]_*" --out "$RESULTS_DIR/summary"
