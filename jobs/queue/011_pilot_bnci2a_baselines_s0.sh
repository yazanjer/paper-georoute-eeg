#!/usr/bin/env bash
# PILOT baselines: BCI IV-2a, LOSO, seed 0, identical folds/splits to GeoRoute.
set -e
cd "$(dirname "$0")/../.."
bash scripts/setup_env.sh
python scripts/run_baselines.py --dataset bnci2014_001 --seed 0 --cv loso --out "$RESULTS_DIR"
python scripts/aggregate.py --inputs "results/01[01]_pilot_bnci2a_*" --out "$RESULTS_DIR/summary"
