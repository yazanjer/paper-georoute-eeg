#!/usr/bin/env bash
# Revision experiments (IJIES review, Nov 2026). One call = one (dataset, seed, model) cell.
#   usage: run_revision.sh DATASET CV SEED MODEL [FOLD_IDS]
#   MODEL: lora | eegnet | fullft | valsubj_lora | valsubj_eegnet
# Conditions (all on the same trained source model, reused through --ckpt-dir):
#   _c1     batch 32, full warm-up (original protocol) + SHOT-IM adapted on the warm-up only (shot_past)
#   _bs1    batch 1 (sample-causal: each trial sees only itself and earlier trials), full warm-up
#   _bs1w0  batch 1, no warm-up (cold start: the stream begins with the scored session)
#   _bs1w32 batch 1, last 32 warm-up trials only;  _bs1w96 (BCI IV-2a) last 96
set -e
DS=$1; CV=$2; SEED=$3; MODEL=$4; FOLDS=${5:-all}
OUT="$RESULTS_DIR"; CK=/workspace/ckpt_rev
case $MODEL in
  lora)   BB="--backbone cbramod --variant lora" ;;
  fullft) BB="--backbone cbramod --variant fullft" ;;
  eegnet) BB="--backbone eegnet" ;;
  valsubj_lora)   BB="--backbone cbramod --variant lora --val-by-subject 1" ;;
  valsubj_eegnet) BB="--backbone eegnet --val-by-subject 1" ;;
esac
COMMON="--dataset $DS --cv $CV --seed $SEED --fold-ids $FOLDS $BB --ckpt-dir $CK --out $OUT --save-preds 1"
GRAD="tent,tent@1e-4"
SHOTP="shot_past,shot_past@1e-5"
if [[ $MODEL == valsubj_* ]]; then
  python scripts/run_tta.py $COMMON --bs 32 --tag _valsubj_c1 \
    --methods source,t3a,lame,$GRAD,shot_im,shot_im@1e-5,$SHOTP
  exit 0
fi
python scripts/run_tta.py $COMMON --bs 32 --tag _c1 --methods source,t3a,lame,$GRAD,shot_im,shot_im@1e-5,$SHOTP
python scripts/run_tta.py $COMMON --bs 1 --tag _bs1   --methods source,t3a,$GRAD,$SHOTP
python scripts/run_tta.py $COMMON --bs 1 --tag _bs1w0 --warmup 0 --methods source,t3a,$GRAD
if [[ $MODEL != fullft ]]; then
  python scripts/run_tta.py $COMMON --bs 1 --tag _bs1w32 --warmup 32 --methods source,t3a,$GRAD,$SHOTP
  if [[ $DS == bnci2014_001 ]]; then
    python scripts/run_tta.py $COMMON --bs 1 --tag _bs1w96 --warmup 96 --methods source,t3a,$GRAD,$SHOTP
  fi
fi
