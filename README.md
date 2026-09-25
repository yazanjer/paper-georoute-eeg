# EEG foundation models vs compact decoders under test-time adaptation

Code, pre-registered protocol and all results for the paper
**"EEG Foundation Models vs Compact Decoders under Test-Time Adaptation: A Pre-Registered Cross-Subject Motor-Imagery Benchmark"** (Y. Aljeroudi, 2026).

Archive: Zenodo, DOI `ZENODO_DOI` (see `.zenodo.json`).

## What is benchmarked

| | |
|---|---|
| Datasets | BCI Competition IV-2a (BNCI2014-001, 9 subjects, 4 classes, LOSO) and Lee2019-MI (54 subjects, 2 classes, 6-fold) via MOABB |
| Backbones | CBraMod (pretrained, frozen) + rank-8 LoRA + MLP head; EEGNet trained from scratch; both with Euclidean alignment |
| TTA methods | source, T3A, LAME, Tent (lr 1e-3, 1e-4), SHOT-IM (lr 1e-4, 1e-5), geo_src (Riemannian MDM), RCTTA, RCTTA+T3A, RCTTA offline |
| Target stream | session 1 = unscored warm-up, last session = scored, batches of 32, online EA, predict-then-update, no target labels |
| Seeds / stats | 5 seeds; per-subject seed-averaged accuracy; Wilcoxon signed-rank, Holm within (dataset, backbone); runs below source |
| Baselines | CSP+LDA, MDM, TS+LR, EEGNet ±EA, ShallowConvNet, EEG-Conformer, CBraMod linear probe / full fine-tune |
| Rejected methods | GeoRoute (covariance-distance routing of subject LoRA adapters), RCTTA (Riemannian co-training) — see `docs/PRIOR_PILOTS.md` |

The protocol and hypotheses H1–H4 were frozen before any benchmark run: `docs/BENCHMARK_PROTOCOL.md`.

## Headline results (accuracy %, mean over subjects of seed-averaged accuracy)

| | BCI IV-2a CBraMod | BCI IV-2a EEGNet+EA | Lee2019 CBraMod | Lee2019 EEGNet+EA |
|---|---|---|---|---|
| Source | 60.3 | 64.4 | 80.7 | 83.6 |
| T3A | 64.0 | 65.1 | 82.5 | 82.5 |
| Tent, lr 1e-3 | 42.8 | 65.8 | 81.0 | 84.2 |
| SHOT-IM, lr 1e-4 | 49.7 | **68.6** | 76.9 | **85.5** |
| SHOT-IM, lr 1e-5 | 64.2 | 65.8 | 83.4 | 84.2 |
| RCTTA + T3A | 64.4 | 65.7 | 82.5 | 82.2 |

Full tables, statistics and figures are in `paper/`.

## Layout

```
src/georoute/        data loading (MOABB), geometry (EA, Riemannian), LoRA, models, training, TTA, RCTTA
scripts/run_tta.py         online TTA benchmark (all methods, one backbone, one seed)
scripts/run_baselines.py   source-model baselines
scripts/run_georoute.py    GeoRoute (stage 1/2 adapters + routing and controls)
scripts/aggregate.py       summaries and paired statistics
scripts/zenodo_deposit.py  Zenodo draft deposition (create / upload; never publishes)
jobs/queue/*.sh            every job exactly as run (one file = one job)
results/<job>/             per-subject JSON results, logs, commit hash, start/finish times
paper/                     LaTeX sources, bibliography, figure script and per-subject data (agg.json)
runner/agent.sh            pull-based GPU worker used on RunPod
```

## Reproducing

```bash
pip install -r requirements.txt
# e.g. BCI IV-2a, CBraMod, seed 0, frozen method set
python scripts/run_tta.py --dataset bnci2014_001 --backbone cbramod --seed 0 --cv loso --methods bench --out results/local
# Lee2019, EEGNet, seed 3
python scripts/run_tta.py --dataset lee2019_mi --backbone eegnet --seed 3 --cv kfold:6 --methods bench --out results/local
python scripts/aggregate.py
```

Each job in `jobs/queue/` lists the exact command, and each `results/<job>/commit` records the git commit that produced it.
Trained weights are not distributed; source models are re-trained by the scripts above (30 epochs for CBraMod-LoRA, 100 for EEGNet).

## Execution on RunPod

A pod started from the `georoute-agent` template clones this repository with the RunPod secret `github_token` and runs `runner/agent.sh`, which polls `main`, runs every `jobs/queue/<name>.sh` that has no `results/<name>/status` (optionally pinned with `# worker: X`), and pushes results back.

## License

MIT (code). Datasets are subject to their original licences (BNCI Horizon 2020; GigaScience OpenBMI).
