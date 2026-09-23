#!/usr/bin/env bash
# PILOT (dev set) for RCTTA with a compact backbone (EEGNet + EA): does the method generalise
# beyond foundation models?  Same stream protocol as 040.
set -e
cd "$(dirname "$0")/../.."
bash scripts/setup_env.sh
python scripts/run_tta.py --dataset bnci2014_001 --seed 0 --cv loso --backbone eegnet --out "$RESULTS_DIR"
python scripts/aggregate.py --inputs "results/04[01]_pilot_bnci2a_tta_*" --ref rctta_cbramod --out "$RESULTS_DIR/summary"
