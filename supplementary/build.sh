#!/usr/bin/env bash
# Rebuild supplementary/supplementary.pdf from the result files of this repository.
# Needs: python3 with numpy, scipy, matplotlib, pillow; a TeX Live with the publishers (elsarticle), science
# and pictures collections; the Liberation Serif font (fonts-liberation).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 scripts/revision_stats.py                 # paper/revision/*.json and unrounded_tta.csv
python3 scripts/revision_new_stats.py             # paper/revision/new_stats.json (supplementary runs, jobs 397-491)
python3 paper/curves/build_curves.py              # paper/curves/curves.json (seed-0 training curves)
python3 paper/revision/make_rev_figs.py paper/revision/figures
W="$ROOT/supplementary/_work"; rm -rf "$W"; mkdir -p "$W/figures"
cp paper/revision/figures/*.pdf "$W/figures/"
cd "$ROOT/supplementary/tikz"
for f in fig_*.tex; do pdflatex -interaction=nonstopmode -output-directory "$W" "$f" >/dev/null; cp "$W/${f%.tex}.pdf" "$W/figures/"; done
cd "$W"
cp "$ROOT"/supplementary/{supplementary.tex,refs.bib} .
pdflatex -interaction=nonstopmode supplementary.tex >/dev/null || true
bibtex supplementary >/dev/null || true
pdflatex -interaction=nonstopmode supplementary.tex >/dev/null || true
pdflatex -interaction=nonstopmode supplementary.tex > build.log || true
grep -E "^!" build.log && exit 1 || true
cp supplementary.pdf "$ROOT/supplementary/supplementary.pdf"
echo "built $(ls -la "$ROOT/supplementary/supplementary.pdf")"
