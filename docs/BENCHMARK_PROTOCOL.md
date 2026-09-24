# Benchmark protocol (frozen 2026-09-24, before any benchmark run)

**Question.** For calibration-free cross-subject motor-imagery decoding, does a pretrained EEG
foundation model (CBraMod) beat a compact aligned decoder (EEGNet + Euclidean alignment), and which
test-time adaptation (TTA) methods actually help each of them?

This protocol was written after two pre-registered method pilots failed (GeoRoute, RCTTA; see
`docs/PRIOR_PILOTS.md` and `results/0*`). Those pilots used BCI IV-2a seed 0 only; everything below is
fixed in advance and is not tuned on any benchmark result.

## Data
| Dataset | Subjects | Classes | Channels | Split |
|---|---|---|---|---|
| BCI IV-2a (BNCI2014-001) | 9 | 4 | 22 | leave-one-subject-out |
| Lee2019-MI (OpenBMI) | 54 | 2 | 62 | 6-fold cross-subject (fixed fold assignment, rng 1234) |
Preprocessing: MOABB MotorImagery paradigm, 0.5–45 Hz, 200 Hz, 0–4 s, µV/100.

## Source models (trained on source subjects only, per fold)
- CBraMod (braindecode/cbramod-pretrained) + global LoRA (rank 8, FFN + projection) + MLP head, 30 epochs.
- EEGNet (braindecode), 100 epochs, early stopping on a 10 % source validation split.
- Source subjects are Euclidean-aligned per subject.
- Source-model baselines (no TTA): CSP+LDA (EA), MDM (RA), TS+LR (RA), EEGNet ±EA, ShallowConvNet (EA),
  EEG-Conformer (EA), CBraMod linear probe (EA), CBraMod full fine-tune (EA).

## Target stream (identical for all TTA methods)
Session 1 of the target subject (unscored warm-up) followed by the last session (scored), chronological,
batch 32. Euclidean alignment is computed online from past + current trials. Online methods predict
before they update. No target labels are ever used.

## TTA methods (frozen set `--methods bench`)
| Method | Type | Setting |
|---|---|---|
| source | none | — |
| T3A | backprop-free, online | filter K = 20 |
| LAME | backprop-free, online | kNN k = 5, 10 iters |
| Tent | gradient, online | SGD m = 0.9, lr 1e-3 **and** 1e-4 (both reported) |
| SHOT-IM | gradient, offline on whole stream | Adam, 10 epochs, lr 1e-4 **and** 1e-5 (both reported) |
| RCTTA (ours, negative) | backprop-free, online | λ = 1, n0 = 20, 8–30 Hz |
| RCTTA + T3A | backprop-free, online | as above |
| RCTTA offline | transductive | as above |
| geo_src | Riemannian MDM, online re-centring | 8–30 Hz |
Two learning rates are pre-specified for gradient methods because no target labels exist to select one;
reporting both exposes the sensitivity instead of hiding it.

## Seeds and statistics
- 5 seeds (0–4) for every TTA × backbone × dataset cell. GeoRoute: seeds 0–2 on BCI IV-2a, seed 0 on
  Lee2019. Source-model baselines: seeds 0–2 on BCI IV-2a, seed 0 on Lee2019.
- Primary metric: accuracy on the scored session; also balanced accuracy and Cohen's κ.
- Per-subject accuracy is averaged over seeds; methods are compared with the two-sided Wilcoxon
  signed-rank test over subjects, Holm-corrected within each (dataset, backbone) family; effect size =
  matched-pairs rank-biserial correlation. Seed-to-seed SD is reported separately.

## Primary hypotheses (directional, stated before the runs)
H1  EEGNet+EA source ≥ CBraMod-LoRA source on both datasets.
H2  T3A improves CBraMod on both datasets.
H3  Gradient TTA (Tent/SHOT) is less stable on CBraMod than on EEGNet (more subjects below source).
H4  Neither covariance-based routing (GeoRoute) nor covariance-based co-training (RCTTA) adds ≥ 1.5 pp
    over the best geometry-free alternative.
Any outcome is reported, including hypotheses that fail.
