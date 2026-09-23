#!/usr/bin/env bash
# CONFIRMATION RUN (last chance for routing): GeoRoute on Lee2019-MI, 6-fold cross-subject
# (9 targets per fold, 45 source subjects each), seed 0, same config as the BCI IV-2a pilot.
# Routing trials = target session 1 (unlabeled), evaluation = target session 2.
#
# PRE-REGISTERED GO CRITERION (fixed before seeing any Lee2019 result):
#   GO if  georoute (merge)  OR  georoute_ens (output ensemble)  beats BOTH its uniform and
#   random-routing counterparts by >= 1.0 pp mean accuracy with Wilcoxon p < 0.05 (54 subjects),
#   AND mean Spearman(distance, single-adapter transfer) >= 0.2.
#   Otherwise NO-GO: routing is dropped and the project pivots.
set -e
cd "$(dirname "$0")/../.."
bash scripts/setup_env.sh
python scripts/run_georoute.py --dataset lee2019_mi --seed 0 --cv kfold:6 --n-route 10,all \
  --out "$RESULTS_DIR"
python scripts/aggregate.py --inputs "$RESULTS_DIR" --out "$RESULTS_DIR/summary"
python scripts/aggregate.py --inputs "$RESULTS_DIR" --ref georoute_ens --out "$RESULTS_DIR/summary_ens"
