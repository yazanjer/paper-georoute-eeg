# Trained model weights (seed 0)

The Zenodo record [10.5281/zenodo.22965131](https://doi.org/10.5281/zenodo.22965131) contains the source models trained in the
seed-0 convergence re-run (jobs `300`, `301`, `303`, `305`–`309`; frozen benchmark settings, `--save-preds 1`). The five-seed benchmark models were
not kept; these seed-0 models reproduce the seed-0 cells of the benchmark up to GPU non-determinism.

| Archive | Dataset / split | Backbone(s) | Files |
|---|---|---|---|
| `models-bnci2a-seed0.zip` | BCI IV-2a (BNCI2014-001), LOSO, 9 folds | CBraMod-LoRA and EEGNet+EA | `bnci2014_001_{cbramod,eegnet}_s0_loso_f{0..8}.pt` |
| `models-lee2019-cbramod-seed0-f0.zip` | Lee2019-MI, 6-fold, fold 0 | CBraMod-LoRA | `lee2019_mi_cbramod_s0_kfold6_f0.pt` |
| `models-lee2019-cbramod-seed0-f12.zip` | Lee2019-MI, 6-fold, folds 1–2 | CBraMod-LoRA | `lee2019_mi_cbramod_s0_kfold6_f{1,2}.pt` |
| `models-lee2019-cbramod-seed0-f345.zip` | Lee2019-MI, 6-fold, folds 3–5 | CBraMod-LoRA | `lee2019_mi_cbramod_s0_kfold6_f{3,4,5}.pt` |
| `models-lee2019-eegnet-seed0-f01.zip` | Lee2019-MI, 6-fold, folds 0–1 | EEGNet+EA | `lee2019_mi_eegnet_s0_kfold6_f{0,1}.pt` |
| `models-lee2019-eegnet-seed0-f23.zip` | Lee2019-MI, 6-fold, folds 2–3 | EEGNet+EA | `lee2019_mi_eegnet_s0_kfold6_f{2,3}.pt` |
| `models-lee2019-eegnet-seed0-f45.zip` | Lee2019-MI, 6-fold, folds 4–5 | EEGNet+EA | `lee2019_mi_eegnet_s0_kfold6_f{4,5}.pt` |

Each archive holds PyTorch `state_dict` files and a `SHA256SUMS.txt`. Fold `k` of BCI IV-2a holds out subject `k+1`. The Lee2019 fold membership is fixed by `folds()` in `scripts/run_tta.py`
(6-fold split of the 54 subjects seeded with the run seed); the held-out subjects of each fold are also recorded in the
per-subject result files of jobs `303` and `305`–`309` (`fold`, `target`).

CBraMod checkpoints contain the full model (frozen pretrained CBraMod weights from braindecode, rank-8 LoRA on `linear1`,
`linear2`, `proj_out.0`, and the MLP head). EEGNet checkpoints are braindecode EEGNet (F1=8, D=2, F2=16) trained on EA-aligned data.

## Using a checkpoint

`scripts/run_tta.py` loads a checkpoint instead of training when it finds one in `--ckpt-dir`:

```bash
unzip models-bnci2a-seed0.zip -d ckpt
python scripts/run_tta.py --dataset bnci2014_001 --backbone cbramod --seed 0 --cv loso \
  --methods source,t3a,tent,shot_im --ckpt-dir ckpt --out results/local
```

Licence: MIT (code and weights). The pretrained CBraMod weights keep their original licence.
