# Figure and table scripts for the manuscript

Scripts that regenerate every figure and derived data file of the manuscript (IEEE TNSRE submission) from the committed
results. The LaTeX sources themselves are distributed with the submission package.

```bash
cd paper
python build_agg.py              # ../results -> agg.json (seed-averaged per-subject accuracy, benchmark jobs only)
python curves/build_curves.py    # ../results/30x -> curves/curves.json (seed-0 re-run: training histories, online accuracy)
python make_figs.py              # fig_delta, fig_below, fig_georoute
python make_figs2.py             # heatmaps, pairwise win-rate, critical-difference, forest plot (+ cd_info.json)
python make_curves.py            # fig_conv_train, fig_conv_online
```
