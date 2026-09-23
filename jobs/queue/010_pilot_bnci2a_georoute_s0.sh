#!/usr/bin/env bash
# PILOT (go/no-go): BCI IV-2a, LOSO, seed 0. GeoRoute + all routing ablations.
# Go criteria: georoute > uniform_merge and > shared_only on mean acc,
#              and mean Spearman(distance, transfer) > 0.
set -e
cd "$(dirname "$0")/../.."
bash scripts/setup_env.sh
python scripts/run_georoute.py --dataset bnci2014_001 --seed 0 --cv loso --out "$RESULTS_DIR"
python scripts/aggregate.py --inputs "$RESULTS_DIR" --out "$RESULTS_DIR/summary"
