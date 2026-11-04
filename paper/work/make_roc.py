import json, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams.update({
    'font.family':'serif', 'font.serif':['DejaVu Serif'], 'font.size':8,
    'axes.labelsize':8, 'axes.titlesize':8, 'legend.fontsize':6.6,
    'xtick.labelsize':7, 'ytick.labelsize':7, 'axes.linewidth':0.7,
    'axes.grid':True, 'grid.linewidth':0.35, 'grid.alpha':0.45, 'grid.linestyle':':',
    'figure.dpi':600, 'savefig.bbox':'tight', 'savefig.pad_inches':0.02,
})
roc = json.load(open('roc_extracted.json'))
res = json.load(open('results.json'))
pc  = res['per_class']
NAMES = {'Normal':'Normal','Pneumonia':'Pneumonia','Cardiomegaly':'Cardiomegaly','Pleural_Effusion':'Pleural effusion'}
COL   = {'Normal':'#1f4e79','Pneumonia':'#c0392b','Cardiomegaly':'#1e8449','Pleural_Effusion':'#b9770e'}

fig, ax = plt.subplots(figsize=(3.4,2.75))
for k in NAMES:
    f = np.array(roc[k]['fpr']); t = np.array(roc[k]['tpr'])
    ax.plot(f, t, lw=1.25, color=COL[k],
            label=f"{NAMES[k]} ({pc[k]['reported_auc']:.3f})")
ax.plot([0,1],[0,1], ls='--', lw=0.8, color='0.35', label='Chance (0.500)')
ax.set_xlim(0,1); ax.set_ylim(0,1.005)
ax.set_xlabel('False positive rate'); ax.set_ylabel('True positive rate')
ax.legend(loc='lower right', frameon=True, framealpha=0.95, borderpad=0.35, handlelength=1.6,
          labelspacing=0.28)
ax.set_title('Held-out test set ($n=830$)', fontsize=8, pad=3)
for s in ('top','right'): ax.spines[s].set_visible(False)
fig.savefig('/home/user/changes/paper/figures/fig_roc.png', dpi=600)
print('fig_roc.png written')
