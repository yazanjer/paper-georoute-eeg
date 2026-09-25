import json, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'serif','font.serif':['Liberation Serif','TeX Gyre Termes','DejaVu Serif'],'font.size':8,
  'axes.linewidth':0.6,'axes.edgecolor':'#52514e','axes.labelcolor':'#0b0b0b','xtick.color':'#52514e','ytick.color':'#52514e',
  'xtick.major.width':0.6,'ytick.major.width':0.6,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'legend.frameon':False})
import os; os.makedirs('figures',exist_ok=True)
A=json.load(open('agg.json'))
C={'cbramod':'#2a78d6','eegnet':'#eb6834'}; GRID='#e4e3df'; INK2='#52514e'
LBL={'cbramod':'CBraMod-LoRA','eegnet':'EEGNet+EA'}
def vec(d,subs): return np.array([d[str(s)] for s in subs])
# sanity check vs tables
for k in ['tta_bnc_cbramod','tta_bnc_eegnet','tta_lee_cbramod','tta_lee_eegnet']:
    print(k, {m:round(np.mean(list(v.values())),1) for m,v in A[k].items()})

# ---- Fig 2: per-subject delta vs source
M=[('t3a','T3A'),('lame','LAME'),('tent','Tent 1e-3'),('tent@1e-4','Tent 1e-4'),('shot_im','SHOT-IM 1e-4'),('shot_im@1e-5','SHOT-IM 1e-5'),('rctta+t3a','RCTTA+T3A')]
fig,axes=plt.subplots(1,2,figsize=(7.16,2.9),sharey=True)
rng=np.random.default_rng(0)
for ax,(ds,title,n) in zip(axes,[('bnc','BCI IV-2a (9 subjects)',9),('lee','Lee2019-MI (54 subjects)',54)]):
    subs=range(1,n+1)
    for i,(m,name) in enumerate(M):
        for j,bb in enumerate(['cbramod','eegnet']):
            d=A[f'tta_{ds}_{bb}']; delta=vec(d[m],subs)-vec(d['source'],subs)
            y=i+(-0.18 if j==0 else 0.18)
            jit=rng.uniform(-0.08,0.08,len(delta))
            ax.scatter(delta,y+jit,s=9 if n==9 else 5,color=C[bb],alpha=0.55 if n>9 else 0.8,linewidths=0,zorder=3)
            ax.plot([delta.mean()]*2,[y-0.14,y+0.14],color=C[bb],lw=2,solid_capstyle='round',zorder=4)
    ax.axvline(0,color=INK2,lw=0.8,zorder=2)
    ax.set_yticks(range(len(M))); ax.set_yticklabels([x[1] for x in M])
    ax.grid(axis='x',color=GRID,lw=0.5,zorder=0); ax.set_axisbelow(True)
    ax.set_title(title,fontsize=8.5,color='#0b0b0b'); ax.set_xlabel('Accuracy change vs. same-backbone source (points)')
    ax.tick_params(axis='y',length=0)
from matplotlib.lines import Line2D
h=[Line2D([],[],marker='o',ls='',color=C[b],ms=4,label=LBL[b]) for b in C]+[Line2D([],[],color=INK2,lw=2,label='mean over subjects')]
axes[0].invert_yaxis()
fig.legend(handles=h,loc='upper center',ncol=3,bbox_to_anchor=(0.55,1.02),fontsize=7.5)
fig.tight_layout(rect=(0,0,1,0.93)); fig.savefig('figures/fig_delta.pdf'); plt.close(fig)

# ---- Fig 3: runs below source (%) from Tables 2-3
rb={'bnc':{'cbramod':[7,36,39,17,37,16,8],'eegnet':[19,45,10,8,6,12,17],'N':45},
    'lee':{'cbramod':[71,157,85,99,166,77,74],'eegnet':[132,240,100,99,38,62,140],'N':270}}
fig,axes=plt.subplots(2,1,figsize=(3.5,3.6),sharex=True)
x=np.arange(len(M)); w=0.38
for ax,(ds,title) in zip(axes,[('bnc','BCI IV-2a (of 45 runs)'),('lee','Lee2019-MI (of 270 runs)')]):
    for j,bb in enumerate(['cbramod','eegnet']):
        v=100*np.array(rb[ds][bb])/rb[ds]['N']
        ax.bar(x+(j-0.5)*w,v,w-0.04,color=C[bb],label=LBL[bb],zorder=3)
    ax.axhline(50,color=INK2,lw=0.6,ls=(0,(3,2)),zorder=2)
    ax.set_ylim(0,100); ax.set_ylabel('Runs below source (%)'); ax.set_title(title,fontsize=8,loc='left')
    ax.grid(axis='y',color=GRID,lw=0.5,zorder=0)
axes[1].set_xticks(x); axes[1].set_xticklabels([m[1] for m in M],rotation=35,ha='right')
axes[0].legend(loc='upper right',fontsize=7)
fig.tight_layout(); fig.savefig('figures/fig_below.pdf'); plt.close(fig)

# ---- Fig 4: GeoRoute vs controls, delta vs uniform ensemble
G=[('shared_only','Shared adapter'),('random_ens','Random routing'),('georoute_ens','GeoRoute'),('oracle_best_single','Oracle adapter')]
fig,axes=plt.subplots(1,2,figsize=(3.5,2.1),sharey=True)
for ax,(g,title,n) in zip(axes,[('geo_bci','BCI IV-2a',9),('geo_lee','Lee2019-MI',54)]):
    subs=range(1,n+1); u=vec(A[g]['uniform_ens'],subs)
    for i,(m,name) in enumerate(G):
        dlt=vec(A[g][m],subs)-u
        col='#008300' if m=='oracle_best_single' else '#2a78d6'
        ax.scatter(dlt,i+rng.uniform(-0.12,0.12,n),s=9 if n==9 else 5,color=col,alpha=0.6,linewidths=0,zorder=3)
        ax.plot([dlt.mean()]*2,[i-0.25,i+0.25],color='#0b0b0b',lw=1.6,zorder=4)
    ax.axvline(0,color=INK2,lw=0.8); ax.set_yticks(range(len(G))); ax.set_yticklabels([g_[1] for g_ in G])
    ax.set_title(title,fontsize=8); ax.grid(axis='x',color=GRID,lw=0.5,zorder=0); ax.tick_params(axis='y',length=0)
axes[0].invert_yaxis()
fig.supxlabel('Accuracy change vs. uniform ensemble (points)',fontsize=8,y=0.03)
fig.tight_layout(rect=(0,0.02,1,1)); fig.savefig('figures/fig_georoute.pdf'); plt.close(fig)
print('ok')
