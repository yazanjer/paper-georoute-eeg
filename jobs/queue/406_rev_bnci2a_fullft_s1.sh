#!/usr/bin/env bash
# REVISION (IJIES 20267270): BCI IV-2a seed 1, CBraMod matched full fine-tuning (re-queued: the first queue overwrote names)
# worker: B2
set -e
cd "$(dirname "$0")/../.."
export OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 NUMEXPR_NUM_THREADS=8
bash scripts/setup_env.sh
bash scripts/run_revision.sh bnci2014_001 loso 1 fullft
