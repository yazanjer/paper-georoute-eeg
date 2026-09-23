#!/usr/bin/env bash
# PILOT (dev set) for RCTTA: BCI IV-2a LOSO, seed 0, CBraMod backbone (global LoRA + head).
# Stream = session 1 (unscored warm-up) -> session 2 (scored); online EA; batch 32.
#
# PRE-REGISTERED GO CRITERION (fixed before any RCTTA result on real data):
#   GO if rctta OR rctta+t3a beats EVERY baseline among {t3a, lame, tent} by >= 1.5 pp mean
#   accuracy with >= 6/9 subject wins (CBraMod backbone).  Ablation variants are NOT used
#   to pick the winner.  If GO, the config is frozen and confirmed on Lee2019 (5 seeds).
set -e
cd "$(dirname "$0")/../.."
bash scripts/setup_env.sh
python scripts/run_tta.py --dataset bnci2014_001 --seed 0 --cv loso --backbone cbramod --out "$RESULTS_DIR"
python scripts/aggregate.py --inputs "$RESULTS_DIR" --ref rctta_cbramod --out "$RESULTS_DIR/summary"
