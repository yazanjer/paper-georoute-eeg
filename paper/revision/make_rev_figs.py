"""Revision figures (IJIES format: every letter >= 10 pt at the printed size, no panel letters, no outer borders).

Figures are drawn at their final printed width (full width 17.2 cm = 6.77 in, one column 8.2 cm = 3.23 in) with
10-pt text, and saved as 300-dpi PNG (for the Word manuscript) and PDF. Data come from the unrounded per-run
result files (results/), via scripts/revision_stats.py helpers.
Run from the repository root:  python paper/revision/make_rev_figs.py [outdir]
"""
import glob, itertools, json, os, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib.lines import Line2D
from scipy.stats import rankdata, friedmanchisquare

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import revision_stats as RS  # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'paper', 'revision', 'figures')
os.makedirs(OUT, exist_ok=True)
FULL, COL = 6.77, 3.23
plt.rcParams.update({'font.family': 'serif', 'font.serif': ['Liberation Serif', 'TeX Gyre Termes', 'DejaVu Serif'],
                     'font.size': 10, 'axes.titlesize': 10, 'axes.labelsize': 10, 'xtick.labelsize': 10, 'ytick.labelsize': 10,
                     'legend.fontsize': 10, 'axes.linewidth': 0.6, 'axes.edgecolor': '#52514e', 'xtick.color': '#52514e',
                     'ytick.color': '#52514e', 'pdf.fonttype': 42, 'legend.frameon': False,
                     'axes.spines.top': False, 'axes.spines.right': False, 'mathtext.fontset': 'stix'})
C = {'cbramod': '#2a78d6', 'eegnet': '#eb6834'}
NAME = {'cbramod': 'CBraMod-LoRA', 'eegnet': 'EEGNet+EA'}
DSN = {'bci': 'BCI IV-2a', 'lee': 'Lee2019-MI'}
GRID, INK2 = '#e4e3df', '#52514e'
DIV = LinearSegmentedColormap.from_list('div', ['#a3302f', '#e34948', '#f3b3a8', '#f0efec', '#9ec5f4', '#3987e5', '#184f95'])
M = [('t3a', 'T3A'), ('lame', 'LAME'), ('tent', 'Tent 1e-3'), ('tent@1e-4', 'Tent 1e-4'), ('shot_im', 'SHOT-IM 1e-4 (T)'),
     ('shot_im@1e-5', 'SHOT-IM 1e-5 (T)'), ('rctta', 'RCTTA'), ('rctta+t3a', 'RCTTA+T3A'), ('rctta_offline', 'RCTTA offl. (T)')]
ACC = RS.load_tta()


def subj_mean(ds, bb, m):
    _, _, A = RS.matrix(ACC, ds, bb, m)
    return 100 * np.nanmean(A, 1)


def save(fig, name, width):
    """Save at the printed size; if labels make the tight bounding box wider than the column/page, shrink the
    canvas (never the fonts) and re-save."""
    from PIL import Image
    for _ in range(6):
        for ext in ('png', 'pdf'):
            fig.savefig(os.path.join(OUT, f'{name}.{ext}'), dpi=300, bbox_inches='tight', pad_inches=0.02)
        w = Image.open(os.path.join(OUT, f'{name}.png')).size[0] / 300
        if w <= width + 0.01:
            break
        fw, fh = fig.get_size_inches()
        fig.set_size_inches(fw - (w - width) - 0.03, fh)
        try:
            fig.tight_layout()
        except Exception:
            pass
    plt.close(fig)
    assert w <= width + 0.02, (name, w, width)
    print(f'{name}: {w * 2.54:.2f} cm wide')


# ---------- per-subject change vs source (two panels stacked, full width)
def fig_delta():
    MM = [x for x in M if x[0] != 'rctta' and x[0] != 'rctta_offline']
    fig, axes = plt.subplots(1, 2, figsize=(FULL, 4.0), sharey=True)
    rng = np.random.default_rng(0)
    for ax, ds in zip(axes, ['bci', 'lee']):
        for i, (m, _) in enumerate(MM):
            for j, bb in enumerate(['cbramod', 'eegnet']):
                d = subj_mean(ds, bb, m) - subj_mean(ds, bb, 'source')
                y = i + (-0.18 if j == 0 else 0.18)
                ax.scatter(d, y + rng.uniform(-0.08, 0.08, len(d)), s=10 if ds == 'bci' else 6, color=C[bb],
                           alpha=0.8 if ds == 'bci' else 0.55, linewidths=0, zorder=3)
                ax.plot([d.mean()] * 2, [y - 0.15, y + 0.15], color=C[bb], lw=2.2, zorder=4)
        ax.axvline(0, color=INK2, lw=0.8)
        ax.set_yticks(range(len(MM))); ax.set_yticklabels([x[1] for x in MM]); ax.tick_params(axis='y', length=0)
        ax.grid(axis='x', color=GRID, lw=0.5); ax.set_axisbelow(True)
        ax.set_title(f'{DSN[ds]} ({9 if ds == "bci" else 54} subjects)')
        ax.set_xlabel('Change vs. source (pp)')
    axes[0].invert_yaxis()
    h = [Line2D([], [], marker='o', ls='', color=C[b], ms=5, label=NAME[b]) for b in C] + \
        [Line2D([], [], color=INK2, lw=2.2, label='Mean over subjects')]
    fig.legend(handles=h, loc='upper center', ncol=3, bbox_to_anchor=(0.55, 1.04))
    fig.tight_layout(rect=(0, 0, 1, 0.93)); save(fig, 'fig_delta', FULL)


# ---------- failure rate with subject-cluster bootstrap CI (one column)
def fig_below():
    MM = [x for x in M if x[0] not in ('rctta', 'rctta_offline')]
    S = json.load(open(os.path.join(ROOT, 'paper', 'revision', 'summary_tta.json')))
    fig, axes = plt.subplots(2, 1, figsize=(COL, 5.6), sharex=True)
    x = np.arange(len(MM)); w = 0.38
    for ax, ds in zip(axes, ['bci', 'lee']):
        for j, bb in enumerate(['cbramod', 'eegnet']):
            e = [S[f'{ds}_{bb}'][m] for m, _ in MM]
            v = np.array([100 * q['failure_rate'] for q in e])
            lo = v - np.array([100 * q['failure_rate_ci'][0] for q in e]); hi = np.array([100 * q['failure_rate_ci'][1] for q in e]) - v
            ax.bar(x + (j - 0.5) * w, v, w - 0.04, color=C[bb], label=NAME[bb], zorder=3)
            ax.errorbar(x + (j - 0.5) * w, v, yerr=[lo, hi], fmt='none', ecolor='#0b0b0b', lw=0.7, capsize=1.5, zorder=4)
        ax.axhline(50, color=INK2, lw=0.6, ls=(0, (3, 2)))
        ax.set_ylim(0, 105); ax.set_ylabel('Runs below source (%)')
        ax.set_title(f'{DSN[ds]} ({45 if ds == "bci" else 270} runs)', loc='left')
        ax.grid(axis='y', color=GRID, lw=0.5)
    axes[1].set_xticks(x); axes[1].set_xticklabels([m[1].replace(' (T)', '') for m in MM], rotation=45, ha='right')
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc='upper center', ncol=1, bbox_to_anchor=(0.55, 1.07))
    fig.tight_layout(rect=(0, 0, 1, 0.93)); save(fig, 'fig_below', COL)


# ---------- GeoRoute vs controls (one column, two stacked panels)
def fig_georoute():
    g = RS.load_geo()
    G = [('shared_only', 'Shared adapter'), ('random_ens', 'Random routing'), ('georoute_ens', 'GeoRoute'), ('oracle_best_single', 'Oracle adapter')]
    fig, axes = plt.subplots(2, 1, figsize=(COL, 4.4), sharex=False)
    rng = np.random.default_rng(1)
    for ax, ds in zip(axes, ['bci', 'lee']):
        for i, (m, lab) in enumerate(G):
            c = g[(ds, m)]; u = g[(ds, 'uniform_ens')]
            keys = sorted(set(c) & set(u)); subs = sorted({s for s, _ in keys})
            d = np.array([100 * np.mean([c[k] - u[k] for k in keys if k[0] == s]) for s in subs])
            col = '#008300' if m == 'oracle_best_single' else '#2a78d6'
            ax.scatter(d, i + rng.uniform(-0.12, 0.12, len(d)), s=10 if ds == 'bci' else 6, color=col, alpha=0.65, linewidths=0, zorder=3)
            ax.plot([d.mean()] * 2, [i - 0.27, i + 0.27], color='#0b0b0b', lw=1.8, zorder=4)
        ax.axvline(0, color=INK2, lw=0.8); ax.set_yticks(range(len(G))); ax.set_yticklabels([x[1] for x in G])
        ax.invert_yaxis(); ax.tick_params(axis='y', length=0); ax.grid(axis='x', color=GRID, lw=0.5)
        ax.set_title(DSN[ds], loc='left')
    axes[1].set_xlabel('Change vs. uniform ensemble (pp)')
    fig.tight_layout(); save(fig, 'fig_georoute', COL)


# ---------- subject x method heatmaps (colour only; two figures)
def heat(ds, name, height):
    lim = 25; norm = TwoSlopeNorm(vcenter=0, vmin=-lim, vmax=lim)
    MM = [x for x in M]
    if ds == 'bci':
        fig, axes = plt.subplots(1, 2, figsize=(FULL - 0.3, height), sharey=True)
        for ax, bb in zip(axes, ['cbramod', 'eegnet']):
            src = subj_mean(ds, bb, 'source')
            D = np.array([subj_mean(ds, bb, m) - src for m, _ in MM])
            im = ax.imshow(np.clip(D, -lim, lim), cmap=DIV, norm=norm, aspect='auto')
            ax.set_xticks(range(9)); ax.set_xticklabels([str(s) for s in range(1, 10)]); ax.set_xlabel('Subject')
            ax.set_yticks(range(len(MM))); ax.set_yticklabels([x[1] for x in MM]); ax.set_title(NAME[bb])
            for sp in ax.spines.values(): sp.set_visible(False)
        cb = fig.colorbar(im, ax=axes, fraction=0.03, pad=0.02); cb.set_label('Change vs. source (pp)'); cb.outline.set_linewidth(0.4)
    else:
        fig, ax = plt.subplots(figsize=(FULL - 1.05, height))
        order = np.argsort(subj_mean('lee', 'eegnet', 'source'))
        rows, labels = [], []
        for bb, tag in [('cbramod', 'CBraMod'), ('eegnet', 'EEGNet')]:
            src = subj_mean('lee', bb, 'source')
            for m, lab in MM:
                rows.append((subj_mean('lee', bb, m) - src)[order]); labels.append(f'{tag}: {lab}')
        im = ax.imshow(np.clip(np.array(rows), -lim, lim), cmap=DIV, norm=norm, aspect='auto')
        ax.axhline(len(MM) - 0.5, color='#0b0b0b', lw=0.9)
        ax.set_yticks(range(len(labels))); ax.set_yticklabels(labels)
        ax.set_xticks(range(0, 54, 6)); ax.set_xticklabels([str(order[j] + 1) for j in range(0, 54, 6)])
        ax.set_xlabel('Subject (sorted by EEGNet+EA source accuracy, every sixth labelled)')
        for sp in ax.spines.values(): sp.set_visible(False)
        cb = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02); cb.set_label('Change vs. source (pp)'); cb.outline.set_linewidth(0.4)
    save(fig, name, FULL)


# ---------- summary heatmap (one column)
def fig_heat_summary():
    cols = [('bci', 'cbramod', 'BCI\nCBraMod'), ('bci', 'eegnet', 'BCI\nEEGNet'), ('lee', 'cbramod', 'Lee\nCBraMod'), ('lee', 'eegnet', 'Lee\nEEGNet')]
    D = np.zeros((len(M), 4)); A = np.zeros((len(M), 4)); S0 = []
    for j, (ds, bb, _) in enumerate(cols):
        src = subj_mean(ds, bb, 'source'); S0.append(src.mean())
        for i, (m, _) in enumerate(M):
            v = subj_mean(ds, bb, m); D[i, j] = (v - src).mean(); A[i, j] = v.mean()
    fig, ax = plt.subplots(figsize=(COL - 0.4, 6.0))
    im = ax.imshow(D, cmap=DIV, norm=TwoSlopeNorm(vcenter=0, vmin=-12, vmax=12), aspect='auto')
    for i in range(len(M)):
        for j in range(4):
            ax.text(j, i, f'{A[i, j]:.1f}\n({round(D[i, j], 1) + 0:+.1f})', ha='center', va='center', fontsize=10,
                    color='white' if abs(D[i, j]) > 8 else '#0b0b0b')
    ax.set_xticks(range(4)); ax.set_xticklabels([c[2] for c in cols]); ax.xaxis.tick_top()
    ax.set_yticks(range(len(M))); ax.set_yticklabels([x[1].replace(' (T)', '') for x in M])
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.set_xlabel('Source: ' + ', '.join(f'{a:.1f}' for a in S0))
    save(fig, 'fig_heat_summary', COL)


# ---------- critical-difference diagrams (full width, 2 x 2)
def fig_cd():
    QA = {10: 3.164}
    ALLM = [('source', 'Source')] + [(m, l.replace(' (T)', '')) for m, l in M]
    short = {'Source': 'Src', 'T3A': 'T3A', 'LAME': 'LAME', 'Tent 1e-3': 'Tent3', 'Tent 1e-4': 'Tent4', 'SHOT-IM 1e-4': 'SHOT4',
             'SHOT-IM 1e-5': 'SHOT5', 'RCTTA': 'RC', 'RCTTA+T3A': 'RC+T3A', 'RCTTA offl.': 'RCoff'}
    fig, axes = plt.subplots(2, 2, figsize=(FULL, 4.6)); axes = axes.ravel(); info = {}
    for ax, (ds, bb) in zip(axes, [('bci', 'cbramod'), ('bci', 'eegnet'), ('lee', 'cbramod'), ('lee', 'eegnet')]):
        X = np.array([subj_mean(ds, bb, m) for m, _ in ALLM]); k, n = X.shape
        R = np.array([rankdata(-X[:, j]) for j in range(n)]).mean(0)
        _, pf = friedmanchisquare(*X); cd = QA[k] * np.sqrt(k * (k + 1) / (6 * n)); info[f'{ds}_{bb}'] = (float(pf), float(cd), R.tolist())
        ax.set_xlim(k + 4.3, -3.3); ax.set_ylim(-0.12, 1.0); AX = 0.86
        ax.hlines(AX, 1, k, color=INK2, lw=0.8)
        for r in range(1, k + 1):
            ax.vlines(r, AX - 0.025, AX + 0.025, color=INK2, lw=0.6); ax.text(r, AX + 0.05, str(r), ha='center', va='bottom')
        order = np.argsort(R); half = k // 2
        for pos, i in enumerate(order):
            left = pos >= half; step = (k - 1 - pos) if left else pos
            y = 0.58 - 0.155 * step; xend = k + 0.3 if left else 0.7
            ax.plot([R[i], R[i], xend], [AX, y, y], color=INK2, lw=0.5)
            ax.text(xend + (0.12 if left else -0.12), y, f'{short[ALLM[i][1]]} ({R[i]:.1f})', ha='right' if left else 'left', va='center')
        srt = sorted(range(k), key=lambda i: R[i]); cl = []
        for a in range(k):
            b = a
            while b + 1 < k and R[srt[b + 1]] - R[srt[a]] <= cd: b += 1
            if b > a and not any(c[0] <= a and c[1] >= b for c in cl): cl.append((a, b))
        for ci, (a, b) in enumerate(cl):
            ax.hlines(AX - 0.07 - 0.035 * ci, R[srt[a]] - 0.05, R[srt[b]] + 0.05, color='#0b0b0b', lw=1.6)
        ax.set_title(f'{DSN[ds]}, {NAME[bb]}: CD = {cd:.2f}', pad=2)
        ax.axis('off')
    fig.subplots_adjust(hspace=0.12, wspace=0.04, left=0.0, right=1.0, top=0.95, bottom=0.0)
    save(fig, 'fig_cd', FULL)
    json.dump(info, open(os.path.join(ROOT, 'paper', 'revision', 'cd_info.json'), 'w'), indent=1)


# ---------- effect-size forest plot (full width)
def rbc(d):
    d = d[d != 0]
    if len(d) == 0: return 0.0
    r = rankdata(np.abs(d)); return (r[d > 0].sum() - r[d < 0].sum()) / r.sum()


def fig_forest():
    rng = np.random.default_rng(0)
    fig, axes = plt.subplots(1, 2, figsize=(FULL, 4.0), sharey=True)
    for ax, ds in zip(axes, ['bci', 'lee']):
        for j, bb in enumerate(['cbramod', 'eegnet']):
            src = subj_mean(ds, bb, 'source')
            for i, (m, _) in enumerate(M):
                d = subj_mean(ds, bb, m) - src; n = len(d); r = rbc(d)
                bs = [rbc(d[rng.integers(0, n, n)]) for _ in range(2000)]
                lo, hi = np.percentile(bs, [2.5, 97.5]); y = i + (-0.17 if j == 0 else 0.17)
                ax.plot([lo, hi], [y, y], color=C[bb], lw=1.3); ax.plot(r, y, 'o', color=C[bb], ms=4.5, mec='white', mew=0.5)
        ax.axvline(0, color=INK2, lw=0.7); ax.set_xlim(-1.05, 1.05)
        ax.set_yticks(range(len(M))); ax.set_yticklabels([x[1] for x in M]); ax.grid(axis='x', color=GRID, lw=0.5)
        ax.set_title(f'{DSN[ds]} ({9 if ds == "bci" else 54} subjects)'); ax.set_xlabel('Rank-biserial r vs. source')
    axes[0].invert_yaxis()
    fig.legend(handles=[Line2D([], [], color=C[b], marker='o', lw=1.3, label=NAME[b]) for b in C],
               loc='upper center', ncol=2, bbox_to_anchor=(0.55, 1.04))
    fig.tight_layout(rect=(0, 0, 1, 0.93)); save(fig, 'fig_forest', FULL)


# ---------- convergence curves (seed-0 re-run)
def fig_conv():
    D = json.load(open(os.path.join(ROOT, 'paper', 'curves', 'curves.json')))
    key = {'bci': 'bnc', 'lee': 'lee'}
    fig, axes = plt.subplots(1, 2, figsize=(FULL, 3.3))
    for ax, ds in zip(axes, ['bci', 'lee']):
        for bb in ['cbramod', 'eegnet']:
            H = [np.array(h) for h in D[f'{key[ds]}_{bb}']['hist'].values()]
            for h in H:
                ax.plot(np.arange(1, len(h) + 1), h[:, 0], color=C[bb], lw=0.4, alpha=0.35)
                ax.plot(np.arange(1, len(h) + 1), h[:, 1], color=C[bb], lw=0.4, alpha=0.35, ls='--')
            L2 = int(np.median([len(h) for h in H]))
            for j, ls in [(0, '-'), (1, '--')]:
                mm = [np.mean([h[e, j] for h in H if len(h) > e]) for e in range(L2)]
                ax.plot(np.arange(1, L2 + 1), mm, color=C[bb], lw=1.5, ls=ls)
        ax.set_title(DSN[ds]); ax.set_xlabel('Epoch'); ax.set_ylabel('Cross-entropy loss'); ax.grid(color=GRID, lw=0.5)
    h = [Line2D([], [], color=C[b], lw=1.5, label=NAME[b]) for b in C] + \
        [Line2D([], [], color=INK2, lw=1.5, label='training'), Line2D([], [], color=INK2, lw=1.5, ls='--', label='validation')]
    fig.legend(handles=h, loc='upper center', ncol=4, bbox_to_anchor=(0.5, 1.05))
    fig.tight_layout(rect=(0, 0, 1, 0.92)); save(fig, 'fig_conv_train', FULL)

    MS = [('t3a', 'T3A', '#2a78d6', '-'), ('rctta+t3a', 'RCTTA+T3A', '#184f95', ':'), ('lame', 'LAME', '#a3302f', '-'),
          ('tent', 'Tent 1e-3', '#eb6834', '-'), ('tent@1e-4', 'Tent 1e-4', '#eb6834', '--'), ('rctta', 'RCTTA', '#52514e', '-')]
    fig, axes = plt.subplots(2, 2, figsize=(FULL, 5.8))
    for r, ds in enumerate(['bci', 'lee']):
        for c, bb in enumerate(['cbramod', 'eegnet']):
            ax = axes[r, c]; g = D[f'{key[ds]}_{bb}']
            Bk = {k: np.array(v) * 100 for k, v in g['blocks'].items()}; bs = g['bs']; nfull = g['n_stream'] // bs
            x = (np.arange(nfull) + 1) * bs
            for m, lab, col, ls in MS:
                ax.plot(x, Bk[m][:nfull] - Bk['source'][:nfull], color=col, ls=ls, lw=1.1, marker='o', ms=2.5, label=lab)
            ax.axhline(0, color='#0b0b0b', lw=0.6); ax.axvspan(0, g['n_warmup'], color='#f1f0ec', zorder=0)
            ax.set_title(f'{DSN[ds]}, {NAME[bb]}'); ax.set_xlim(0, x[-1] + bs / 2)
            ax.set_xlabel('Trials streamed'); ax.set_ylabel('Change vs. source (pp)'); ax.grid(color=GRID, lw=0.5)
    h, l = axes[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc='upper center', ncol=3, bbox_to_anchor=(0.5, 1.06))
    fig.tight_layout(rect=(0, 0, 1, 0.93)); save(fig, 'fig_conv_online', FULL)


def fig_warmup():
    p = os.path.join(ROOT, 'paper', 'revision', 'new_stats.json')
    if not os.path.exists(p): return
    N = json.load(open(p)); CD = N.get('cold', {})
    if not CD: return
    fig, axes = plt.subplots(1, 2, figsize=(FULL, 3.4))
    sty = {'source': ('-', 'Source'), 't3a': ('-.', 'T3A'), 'tent@1e-4': (':', 'Tent 1e-4')}
    for ax, ds in zip(axes, ['bci', 'lee']):
        for mdl, bb in (('lora', 'cbramod'), ('eegnet', 'eegnet')):
            c0 = CD.get(f'{ds}|{mdl}|bs1w0'); cf = CD.get(f'{ds}|{mdl}|bs1')
            if not c0: continue
            for m, (ls, lab) in sty.items():
                if m in c0:
                    ax.plot(c0[m]['k'], c0[m]['acc'], color=C[bb], ls=ls, lw=1.4)
            if cf and 'source' in cf:
                ax.axhline(cf['source']['acc'][-1], color=C[bb], lw=0.9, ls=(0, (5, 3)), alpha=0.7)
        ax.set_title(DSN[ds]); ax.set_xlabel('Scored trials seen (k)'); ax.set_ylabel('Accuracy over first k trials (%)')
        ax.grid(color=GRID, lw=0.5)
    h = [Line2D([], [], color=C[b], lw=1.4, label=NAME[b]) for b in C] + \
        [Line2D([], [], color=INK2, lw=1.4, ls=ls, label=lab) for m, (ls, lab) in sty.items()] + \
        [Line2D([], [], color=INK2, lw=0.9, ls=(0, (5, 3)), label='Source, full warm-up')]
    fig.legend(handles=h, loc='upper center', ncol=3, bbox_to_anchor=(0.5, 1.12))
    fig.tight_layout(rect=(0, 0, 1, 0.97)); save(fig, 'fig_warmup', FULL)


if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[2] == 'warmup':
        fig_warmup(); sys.exit(0)
    fig_warmup()
    for f in (fig_delta, fig_below, fig_georoute, lambda: heat('bci', 'fig_heat_bci', 3.0),
              lambda: heat('lee', 'fig_heat_lee', 5.2), fig_heat_summary, fig_cd, fig_forest, fig_conv):
        f()
