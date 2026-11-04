#!/usr/bin/env bash
# REVISION (IJIES 20267270): audit that target labels are used only for scoring (synthetic + BCI IV-2a, CPU; v2: separate source models per pass)
# worker: B1
set -e
cd "$(dirname "$0")/../.."
export OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 NUMEXPR_NUM_THREADS=8
bash scripts/setup_env.sh
python scripts/check_label_isolation.py | tee "$RESULTS_DIR/label_isolation_synthetic.txt"
python scripts/check_label_isolation.py --dataset bnci2014_001 --cv loso --fold-ids 0 --backbone eegnet --epochs 3 --bs 32 | tee "$RESULTS_DIR/label_isolation_bnci2a_eegnet.txt"
