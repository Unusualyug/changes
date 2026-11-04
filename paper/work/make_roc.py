"""ROC figure.
Normal / Pneumonia / Pleural effusion: coordinates recovered from the committed
evaluation figure (the pipeline never wrote numeric curve points).
Cardiomegaly: the committed curve provably does not correspond to this run
(AUC 0.957 with TPR 0.96 at FPR 0.137, against a verified operating point of
TPR 0.479), so panel (b) is DERIVED from the verified count matrix instead and is
labelled as a bracket, not as a measured curve.
"""
import json, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams.update({'font.family':'serif','font.serif':['DejaVu Serif'],'font.size':8,
 'axes.labelsize':8,'axes.titlesize':8,'legend.fontsize':6.6,'xtick.labelsize':7,
 'ytick.labelsize':7,'axes.linewidth':0.7,'axes.grid':True,'grid.linewidth':0.35,
 'grid.alpha':0.45,'grid.linestyle':':','figure.dpi':600,'savefig.bbox':'tight',
 'savefig.pad_inches':0.02})
roc=json.load(open('roc_extracted.json')); res=json.load(open('results.json'))
pc=res['per_class']
NM={'Normal':'Normal','Pneumonia':'Pneumonia','Pleural_Effusion':'Pleural effusion'}
COL={'Normal':'#1f4e79','Pneumonia':'#c0392b','Pleural_Effusion':'#b9770e'}

fig, axes = plt.subplots(1,2, figsize=(6.9,2.85),
                         gridspec_kw={'width_ratios':[1.32,1]})

ax=axes[0]
for k in ['Normal','Pneumonia','Pleural_Effusion']:
    f=np.array(roc[k]['fpr']); t=np.array(roc[k]['tpr'])
    ax.plot(f,t,lw=1.2,color=COL[k],label=f"{NM[k]} ({pc[k]['reported_auc']:.3f})")
ax.plot([0,1],[0,1],ls='--',lw=0.8,color='0.35',label='Chance (0.500)')
ax.set_xlim(0,1); ax.set_ylim(0,1.005)
ax.set_xlabel('False positive rate'); ax.set_ylabel('True positive rate')
ax.set_title('(a) Curves recovered from the archived evaluation figure', fontsize=7.6, pad=3)
ax.legend(loc='lower right',frameon=True,framealpha=0.95,borderpad=0.3,
          handlelength=1.5,labelspacing=0.25)
for s in ('top','right'): ax.spines[s].set_visible(False)

ax=axes[1]
d=pc['Cardiomegaly']
M=np.array([[d['tn'],d['fp']],[d['fn'],d['tp']]],float)
# attainable (FPR,TPR) at the fixed threshold is bracketed by two extreme curves
fpr_op=d['fp']/(d['fp']+d['tn']); tpr_op=d['tp']/(d['tp']+d['fn'])
ax.plot([0,fpr_op,fpr_op,1],[0,0,tpr_op,1],lw=1.0,color='#1e8449',ls=':',
        label='upper bracket (AUC %.3f)'%(0.5*(1+(1-fpr_op)*tpr_op)))
ax.plot([0,0,fpr_op,1],[0,tpr_op,tpr_op,1],lw=1.0,color='#1e8449',
        label='lower bracket (AUC %.3f)'%(0.5*(1+fpr_op*(1-tpr_op))))
ax.plot([fpr_op],[tpr_op],marker='o',ms=3.6,mfc='#8a1c12',mec='#8a1c12',zorder=5,
        label=f"verified operating point\n(FPR {fpr_op:.3f}, TPR {tpr_op:.3f})")
ax.plot([0,1],[0,1],ls='--',lw=0.8,color='0.35')
ax.axhline(0.959,xmin=0,xmax=0.02,color='none')
ax.annotate('archived curve passes here\n(TPR 0.959 at this FPR): impossible\nfor the verified counts',
            xy=(fpr_op,0.959), xytext=(0.42,0.86), fontsize=6.2, color='#8a1c12',
            ha='left', va='center',
            arrowprops=dict(arrowstyle='->',lw=0.7,color='#8a1c12'))
ax.plot([fpr_op],[0.959],marker='x',ms=5,color='#8a1c12',mew=1.0)
ax.set_xlim(0,1); ax.set_ylim(0,1.005)
ax.set_xlabel('False positive rate'); ax.set_ylabel('True positive rate')
ax.set_title('(b) Cardiomegaly: AUC bracket implied by verified counts', fontsize=7.6, pad=3)
ax.legend(loc='lower right',frameon=True,framealpha=0.95,borderpad=0.3,
          handlelength=1.5,labelspacing=0.3,fontsize=5.9)
for s in ('top','right'): ax.spines[s].set_visible(False)

fig.tight_layout(w_pad=1.5)
fig.savefig('/home/user/changes/paper/figures/fig_roc.png', dpi=600)
print('fig_roc.png written; Cardiomegaly verifiable AUC band: %.3f - %.3f'
      % (0.5*(1+fpr_op*(1-tpr_op)), 0.5*(1+(1-fpr_op)*tpr_op)))
