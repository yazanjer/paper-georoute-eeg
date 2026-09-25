"""Convergence figures from the seed-0 re-run (jobs 300, 301, 303, 305-309): source training curves and online accuracy vs. trials."""
import json, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'serif','font.serif':['Liberation Serif','TeX Gyre Termes','DejaVu Serif'],'font.size':7.5,
  'axes.linewidth':0.6,'axes.edgecolor':'#52514e','xtick.color':'#52514e','ytick.color':'#52514e','pdf.fonttype':42})
D = json.load(open('curves/curves.json'))
C = {'cbramod': '#2a78d6', 'eegnet': '#eb6834'}
NAME = {'cbramod': 'CBraMod-LoRA', 'eegnet': 'EEGNet+EA'}
DS = {'bnc': 'BCI IV-2a', 'lee': 'Lee2019-MI'}

# ---- 1. source-model training curves (train and validation loss per epoch, every fold)
fig, axes = plt.subplots(1, 2, figsize=(7.16, 2.3))
for ax, ds in zip(axes, ['bnc', 'lee']):
    for bb in ['cbramod', 'eegnet']:
        g = D.get(f'{ds}_{bb}')
        if not g: continue
        H = [np.array(h) for h in g['hist'].values()]
        for h in H:
            ax.plot(np.arange(1, len(h) + 1), h[:, 0], color=C[bb], lw=0.4, alpha=0.35)
            ax.plot(np.arange(1, len(h) + 1), h[:, 1], color=C[bb], lw=0.4, alpha=0.35, ls='--')
        L = max(len(h) for h in H)
        for j, ls in [(0, '-'), (1, '--')]:
            L2 = int(np.median([len(h) for h in H]))  # mean only while at least half of the folds are still training
            m = [np.mean([h[e, j] for h in H if len(h) > e]) for e in range(L2)]
            ax.plot(np.arange(1, L2 + 1), m, color=C[bb], lw=1.4, ls=ls,
                    label=f'{NAME[bb]} {"train" if j == 0 else "val"}')
    ax.set_title(f'{DS[ds]} (seed 0, one line per fold)', fontsize=8); ax.set_xlabel('Epoch'); ax.set_ylabel('Cross-entropy loss')
    ax.grid(color='#e4e3df', lw=0.5); ax.spines[['top', 'right']].set_visible(False)
axes[1].legend(frameon=False, fontsize=6.5, ncol=2)
fig.tight_layout(); fig.savefig('figures/fig_conv_train.pdf'); plt.close(fig)

# ---- 2. online accuracy vs. trials: per-batch accuracy change vs. source, mean over subjects
MS = [('t3a', 'T3A', '#2a78d6', '-'), ('rctta+t3a', 'RCTTA+T3A', '#184f95', ':'), ('lame', 'LAME', '#a3302f', '-'),
      ('tent', 'Tent 1e-3', '#eb6834', '-'), ('tent@1e-4', 'Tent 1e-4', '#eb6834', '--'), ('rctta', 'RCTTA', '#52514e', '-')]
fig, axes = plt.subplots(2, 2, figsize=(7.16, 4.2))
for r, ds in enumerate(['bnc', 'lee']):
    for c, bb in enumerate(['cbramod', 'eegnet']):
        ax = axes[r, c]; g = D.get(f'{ds}_{bb}')
        if not g: ax.axis('off'); continue
        B = {k: np.array(v) * 100 for k, v in g['blocks'].items()}; bs = g['bs']
        nfull = g['n_stream'] // bs   # drop a final partial batch (Lee2019: 8 trials), too small for LAME/T3A statistics
        B = {k: v[:nfull] for k, v in B.items()}
        x = (np.arange(nfull) + 1) * bs
        for m, lab, col, ls in MS:
            ax.plot(x, B[m] - B['source'], color=col, ls=ls, lw=1.1, marker='o', ms=2, label=lab)
        ax.axhline(0, color='#0b0b0b', lw=0.6)
        ax.axvspan(0, g['n_warmup'], color='#f1f0ec', zorder=0)
        ax.text(g['n_warmup'] / 2, 0.03, 'warm-up session', transform=ax.get_xaxis_transform(), ha='center', va='bottom', fontsize=6, color='#52514e')
        ax.text(g['n_warmup'] + (x[-1] - g['n_warmup']) / 2, 0.03, 'scored session', transform=ax.get_xaxis_transform(), ha='center', va='bottom', fontsize=6, color='#52514e')
        ax.set_title(f'{DS[ds]} · {NAME[bb]} (n = {g["n"]})', fontsize=8)
        ax.set_xlim(0, x[-1] + bs / 2); ax.set_xlabel('Trials seen in the stream'); ax.set_ylabel('Batch accuracy − source (points)')
        ax.grid(color='#e4e3df', lw=0.5); ax.spines[['top', 'right']].set_visible(False)
h, l = axes[0, 0].get_legend_handles_labels()
fig.legend(h, l, loc='upper center', ncol=6, frameon=False, bbox_to_anchor=(0.5, 1.01))
fig.tight_layout(rect=(0, 0, 1, 0.95)); fig.savefig('figures/fig_conv_online.pdf'); plt.close(fig)

# ---- seed-0 check vs. paper-level numbers
out = {}
for k, g in D.items():
    if "accs_summary" in g:
        out[k] = g['accs_summary']; continue
    a = g['accs']; ms = [m for m in next(iter(a.values())) if not (m.startswith('t_') or m == 'train_time_s')]
    out[k] = {'means': {m: round(100 * np.mean([v[m] for v in a.values()]), 1) for m in ms},
              'train_med': round(float(np.median([v['train_time_s'] for v in a.values()])), 1)}
print(json.dumps(out))
