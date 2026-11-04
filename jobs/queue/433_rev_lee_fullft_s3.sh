#!/usr/bin/env bash
# REVISION (IJIES 20267270): Lee2019-MI seed 3, model fullft; protocol sensitivity
# worker: L4
set -e
cd "$(dirname "$0")/../.."
export OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 NUMEXPR_NUM_THREADS=8
bash scripts/setup_env.sh
bash scripts/run_revision.sh lee2019_mi kfold:6 3 fullft
