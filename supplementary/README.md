# Supplementary material

`supplementary.pdf` is the supplementary material of the article
*A Compact Aligned Decoder Versus a LoRA-Adapted CBraMod Foundation Model for Calibration-Free
Motor-Imagery Decoding: A Test-Time Adaptation Benchmark* (International Journal of Intelligent
Engineering and Systems). The article refers to its content as Sections S1–S3, Tables S1–S11,
Figs. S1–S15 and Algorithms S1–S4:

- **S1** Source models, target stream and methods: training settings of every model, information
  access of every method, the stream and TTA algorithms, architecture and protocol figures.
- **S2** The two geometry-based methods (GeoRoute, RCTTA): architectures, algorithms, development
  gates and pilot outcomes.
- **S3** Additional results: per-subject changes, warm-up length, offline source baselines, GeoRoute
  table and sensitivity analysis, per-subject heatmaps, critical-difference and effect-size analyses,
  balanced accuracy, Cohen's kappa and compute, training curves and online dynamics, hypothesis
  verdicts, and per-subject results on BCI IV-2a.

Every number is computed from the result files in `results/`. `build.sh` regenerates the statistics,
the figures and the PDF from those files; `supplementary.tex`, `refs.bib` and `tikz/` are its sources.
