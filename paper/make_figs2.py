"""Heatmaps, pairwise win-rate matrices, critical-difference diagrams and effect-size forest plot (from agg.json)."""
import json, os, itertools, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from scipy.stats import wilcoxon, friedmanchisquare, rankdata
plt.rcParams.update({'font.family':'serif','font.serif':['Liberation Serif','TeX Gyre Termes','DejaVu Serif'],'font.size':7.5,
  'axes.linewidth':0.6,'axes.edgecolor':'#52514e','xtick.color':'#52514e','ytick.color':'#52514e','pdf.fonttype':42})
os.makedirs('figures', exist_ok=True)
A = json.load(open('agg.json'))
DIV = LinearSegmentedColormap.from_list('div', ['#a3302f', '#e34948', '#f3b3a8', '#f0efec', '#9ec5f4', '#3987e5', '#184f95'])
C = {'cbramod': '#2a78d6', 'eegnet': '#eb6834'}
M = [('t3a','T3A'),('lame','LAME'),('tent','Tent 1e-3'),('tent@1e-4','Tent 1e-4'),('shot_im','SHOT-IM 1e-4'),
     ('shot_im@1e-5','SHOT-IM 1e-5'),('rctta','RCTTA'),('rctta+t3a','RCTTA+T3A'),('rctta_offline','RCTTA offl.')]
ALLM = [('source','Source')] + M
PANELS = [('bnc','cbramod','BCI IV-2a · CBraMod-LoRA',9),('bnc','eegnet','BCI IV-2a · EEGNet+EA',9),
          ('lee','cbramod','Lee2019 · CBraMod-LoRA',54),('lee','eegnet','Lee2019 · EEGNet+EA',54)]
def V(ds, bb, m, n): return np.array([A[f'tta_{ds}_{bb}'][m][str(s)] for s in range(1, n + 1)])
def holm(p):
    p = np.asarray(p, float); o = np.argsort(p); out = np.empty_like(p); run = 0
    for i, k in enumerate(o): run = max(run, (len(p) - i) * p[k]); out[k] = min(1, run)
    return out
def rbc(d):
    d = d[d != 0]
    if len(d) == 0: return 0.0
    r = rankdata(np.abs(d)); return (r[d > 0].sum() - r[d < 0].sum()) / r.sum()

# ---------- 1. subject x method delta heatmaps
fig = plt.figure(figsize=(7.16, 4.6))
gs = fig.add_gridspec(2, 3, width_ratios=[9, 9, 1.2], height_ratios=[1, 1], wspace=0.08, hspace=0.45)
axes = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, :2])]
lim = 25; norm = TwoSlopeNorm(vcenter=0, vmin=-lim, vmax=lim)
# BCI panels side by side, Lee panels stacked in one axis (CBraMod rows then EEGNet rows)
for ax, (ds, bb, title, n) in zip(axes[:2], PANELS[:2]):
    src = V(ds, bb, 'source', n); D = np.array([V(ds, bb, m, n) - src for m, _ in M])
    im = ax.imshow(np.clip(D, -lim, lim), cmap=DIV, norm=norm, aspect='auto')
    ax.set_xticks(range(n)); ax.set_xticklabels([f'S{s}' for s in range(1, n + 1)], fontsize=6.5)
    ax.set_yticks(range(len(M))); ax.set_yticklabels([x[1] for x in M] if ax is axes[0] else [])
    ax.set_title(title, fontsize=8)
    for i in range(D.shape[0]):
        for j in range(D.shape[1]):
            ax.text(j, i, f'{round(D[i, j]) + 0:.0f}', ha='center', va='center', fontsize=5.2, color='#0b0b0b' if abs(D[i, j]) < 15 else 'white')
ax = axes[2]
rows = []; labels = []
order = np.argsort(V('lee', 'eegnet', 'source', 54))  # subjects sorted by EEGNet source accuracy
for bb, tag in [('cbramod', 'CBraMod'), ('eegnet', 'EEGNet')]:
    src = V('lee', bb, 'source', 54)
    for m, lab in M:
        rows.append((V('lee', bb, m, 54) - src)[order]); labels.append(f'{tag}: {lab}')
D = np.array(rows)
im = ax.imshow(np.clip(D, -lim, lim), cmap=DIV, norm=norm, aspect='auto')
ax.axhline(len(M) - 0.5, color='#0b0b0b', lw=0.8)
ax.set_yticks(range(len(labels))); ax.set_yticklabels(labels, fontsize=6)
ax.set_xticks(range(0, 54, 3)); ax.set_xticklabels([f'S{order[j] + 1}' for j in range(0, 54, 3)], fontsize=6)
ax.set_title('Lee2019-MI (54 subjects, sorted by EEGNet+EA source accuracy)', fontsize=8)
cax = fig.add_subplot(gs[:, 2]); cb = fig.colorbar(im, cax=cax); cb.set_label('Accuracy change vs. source (points)')
cb.outline.set_linewidth(0.4)
fig.savefig('figures/fig_heat_subject.pdf', bbox_inches='tight'); plt.close(fig)

# ---------- 2. summary heatmap (methods x panels) with delta annotation
fig, ax = plt.subplots(figsize=(3.5, 3.2))
cols = [('bnc','cbramod',9,'BCI\nCBraMod'),('bnc','eegnet',9,'BCI\nEEGNet'),('lee','cbramod',54,'Lee\nCBraMod'),('lee','eegnet',54,'Lee\nEEGNet')]
D = np.zeros((len(M), 4)); ACC = np.zeros((len(M) + 1, 4))
for j, (ds, bb, n, _) in enumerate(cols):
    src = V(ds, bb, 'source', n); ACC[0, j] = src.mean()
    for i, (m, _) in enumerate(M):
        D[i, j] = (V(ds, bb, m, n) - src).mean(); ACC[i + 1, j] = V(ds, bb, m, n).mean()
im = ax.imshow(D, cmap=DIV, norm=TwoSlopeNorm(vcenter=0, vmin=-12, vmax=12), aspect='auto')
for i in range(len(M)):
    for j in range(4):
        ax.text(j, i, f'{ACC[i + 1, j]:.1f}\n({D[i, j] + 0:+.1f})', ha='center', va='center', fontsize=5.8,
                color='white' if abs(D[i, j]) > 8 else '#0b0b0b')
ax.set_xticks(range(4)); ax.set_xticklabels([c[3] for c in cols], fontsize=6.8)
ax.set_yticks(range(len(M))); ax.set_yticklabels([x[1] for x in M])
ax.set_title('Mean accuracy (Δ vs. source); source = ' + ', '.join(f'{a:.1f}' for a in ACC[0]), fontsize=6.5)
cb = fig.colorbar(im, ax=ax, fraction=0.05, pad=0.03); cb.set_label('Δ (points)'); cb.outline.set_linewidth(0.4)
fig.tight_layout(); fig.savefig('figures/fig_heat_summary.pdf'); plt.close(fig)

# ---------- 3. pairwise win-rate matrices with Holm-significance marks
fig, axes = plt.subplots(1, 4, figsize=(7.16, 2.35))
wr_cmap = LinearSegmentedColormap.from_list('wr', ['#a3302f', '#f3b3a8', '#f0efec', '#9ec5f4', '#184f95'])
short = ['Src', 'T3A', 'LAME', 'Tent3', 'Tent4', 'SHOT4', 'SHOT5', 'RC', 'RC+T3A', 'RCoff']
for ax, (ds, bb, title, n) in zip(axes, PANELS):
    X = np.array([V(ds, bb, m, n) for m, _ in ALLM]); k = len(ALLM)
    W = np.full((k, k), np.nan); P = []; idx = []
    for a, b in itertools.permutations(range(k), 2):
        W[a, b] = np.mean(X[a] > X[b]) + 0.5 * np.mean(X[a] == X[b])
    for a, b in itertools.combinations(range(k), 2):
        d = X[a] - X[b]; P.append(wilcoxon(X[a], X[b]).pvalue if np.any(d) else 1.0); idx.append((a, b))
    PH = holm(P)
    ax.imshow(W, cmap=wr_cmap, vmin=0, vmax=1)
    for (a, b), p in zip(idx, PH):
        if p < 0.05:
            ax.text(b, a, '•', ha='center', va='center', fontsize=6, color='#0b0b0b')
            ax.text(a, b, '•', ha='center', va='center', fontsize=6, color='#0b0b0b')
    ax.set_xticks(range(k)); ax.set_xticklabels(short, rotation=90, fontsize=5.5)
    ax.set_yticks(range(k)); ax.set_yticklabels(short if ax is axes[0] else [], fontsize=5.5)
    ax.set_title(title.replace(' · ', '\n'), fontsize=7)
sm = plt.cm.ScalarMappable(cmap=wr_cmap, norm=plt.Normalize(0, 1))
cb = fig.colorbar(sm, ax=axes, fraction=0.015, pad=0.01); cb.set_label('Row beats column\n(share of subjects)', fontsize=6.5); cb.outline.set_linewidth(0.4)
fig.savefig('figures/fig_pairwise.pdf', bbox_inches='tight'); plt.close(fig)

# ---------- 4. critical-difference diagrams (Friedman + Nemenyi, alpha = 0.05)
QA = {2: 1.960, 3: 2.343, 4: 2.569, 5: 2.728, 6: 2.850, 7: 2.949, 8: 3.031, 9: 3.102, 10: 3.164, 11: 3.219}
fig, axes = plt.subplots(2, 2, figsize=(7.16, 3.6)); axes = axes.ravel()
cd_info = {}
for ax, (ds, bb, title, n) in zip(axes, PANELS):
    X = np.array([V(ds, bb, m, n) for m, _ in ALLM]); k = len(ALLM)
    R = np.array([rankdata(-X[:, j]) for j in range(n)]).mean(0)   # rank 1 = best
    stat, pf = friedmanchisquare(*X)
    cd = QA[k] * np.sqrt(k * (k + 1) / (6 * n)); cd_info[f'{ds}_{bb}'] = (float(pf), float(cd), R.tolist())
    ax.set_xlim(k + 3.2, -2.2); ax.set_ylim(-0.05, 1.22)
    AX = 0.80
    ax.hlines(AX, 1, k, color='#52514e', lw=0.8)
    for r in range(1, k + 1): ax.vlines(r, AX - 0.025, AX + 0.025, color='#52514e', lw=0.6); ax.text(r, AX + 0.05, str(r), ha='center', va='bottom', fontsize=6)
    order = np.argsort(R); half = k // 2
    for pos, i in enumerate(order):
        left = pos >= half          # worse ranks drawn on the left (high rank numbers)
        step = (k - 1 - pos) if left else pos
        y = 0.50 - 0.105 * step
        xend = k + 0.3 if left else 0.7
        ax.plot([R[i], R[i], xend], [AX, y, y], color='#52514e', lw=0.5)
        ax.text(xend + (0.12 if left else -0.12), y, f'{ALLM[i][1]} ({R[i]:.1f})', ha='right' if left else 'left', va='center', fontsize=5.8)
    srt = sorted(range(k), key=lambda i: R[i]); cl = []
    for a in range(k):
        b = a
        while b + 1 < k and R[srt[b + 1]] - R[srt[a]] <= cd: b += 1
        if b > a and not any(c[0] <= a and c[1] >= b for c in cl): cl.append((a, b))
    for ci, (a, b) in enumerate(cl):
        yy = AX - 0.07 - 0.035 * ci
        ax.hlines(yy, R[srt[a]] - 0.05, R[srt[b]] + 0.05, color='#0b0b0b', lw=1.6)
    ax.hlines(AX + 0.22, k, k - cd, color='#0b0b0b', lw=1.0); ax.vlines([k, k - cd], AX + 0.20, AX + 0.24, color='#0b0b0b', lw=0.8)
    ax.text(k - cd / 2, AX + 0.25, f'CD = {cd:.2f}', ha='center', va='bottom', fontsize=5.8)
    ax.set_title(f'{title}   (Friedman p = {pf:.1e}, n = {n})', fontsize=7, pad=1)
    ax.axis('off')
fig.subplots_adjust(hspace=0.18, wspace=0.05, left=0.01, right=0.99, top=0.95, bottom=0.01)
fig.savefig('figures/fig_cd.pdf'); plt.close(fig)
json.dump(cd_info, open('cd_info.json', 'w'), indent=1)

# ---------- 5. effect-size forest plot (rank-biserial r vs source, bootstrap 95% CI)
rng = np.random.default_rng(0)
fig, axes = plt.subplots(1, 2, figsize=(7.16, 2.9), sharey=True)
for ax, ds, ttl, n in [(axes[0], 'bnc', 'BCI IV-2a (9 subjects)', 9), (axes[1], 'lee', 'Lee2019-MI (54 subjects)', 54)]:
    for j, bb in enumerate(['cbramod', 'eegnet']):
        src = V(ds, bb, 'source', n)
        for i, (m, lab) in enumerate(M):
            d = V(ds, bb, m, n) - src; r = rbc(d)
            bs = [rbc(d[rng.integers(0, n, n)]) for _ in range(2000)]
            lo, hi = np.percentile(bs, [2.5, 97.5]); y = i + (-0.17 if j == 0 else 0.17)
            ax.plot([lo, hi], [y, y], color=C[bb], lw=1.2); ax.plot(r, y, 'o', color=C[bb], ms=3.8, mec='white', mew=0.5)
    ax.axvline(0, color='#52514e', lw=0.7); ax.set_xlim(-1.05, 1.05)
    ax.set_yticks(range(len(M))); ax.set_yticklabels([x[1] for x in M]); ax.grid(axis='x', color='#e4e3df', lw=0.5)
    ax.set_title(ttl, fontsize=8); ax.set_xlabel('Rank-biserial r vs. source (95% bootstrap CI)')
    ax.spines[['top', 'right']].set_visible(False)
axes[0].invert_yaxis()
from matplotlib.lines import Line2D
fig.legend(handles=[Line2D([], [], color=C[b], marker='o', lw=1.2, label=l) for b, l in [('cbramod', 'CBraMod-LoRA'), ('eegnet', 'EEGNet+EA')]],
           loc='upper center', ncol=2, frameon=False, bbox_to_anchor=(0.55, 1.03))
fig.tight_layout(rect=(0, 0, 1, 0.94)); fig.savefig('figures/fig_forest.pdf'); plt.close(fig)
print(json.dumps({k: (round(v[0], 6), round(v[1], 2)) for k, v in cd_info.items()}))
