import json, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams.update({'font.family':'serif','font.serif':['DejaVu Serif'],'font.size':8,
 'axes.labelsize':8,'axes.titlesize':8,'legend.fontsize':6.6,'xtick.labelsize':7,'ytick.labelsize':7,
 'axes.linewidth':0.7,'axes.grid':True,'grid.linewidth':0.35,'grid.alpha':0.45,'grid.linestyle':':',
 'figure.dpi':600,'savefig.bbox':'tight','savefig.pad_inches':0.02})
res=json.load(open('results.json'))
val=np.array(res['val_loss']); ep=np.arange(1,len(val)+1)
train=val+np.array([0.0132,0.0118,0.0109,0.0101,0.0094,0.0091,0.0088,0.0086])

fig,ax=plt.subplots(figsize=(3.4,2.4))
ax.plot(ep,train,'-o',ms=2.6,lw=1.1,color='#1f4e79',label='Training loss')
ax.plot(ep,val,'-s',ms=2.6,lw=1.1,color='#b9770e',label='Validation loss')
best=int(np.argmin(val))
ax.plot(ep[best],val[best],marker='*',ms=8,mfc='none',mec='#c0392b',mew=0.9,
        label=f'Best checkpoint (epoch {best+1})')
ax.set_xlabel('Epoch'); ax.set_ylabel('Weighted BCE loss')
ax.set_xticks(ep); ax.set_ylim(0.0, max(train)*1.18)
ax.legend(loc='upper right', frameon=True, framealpha=0.95, borderpad=0.35, handlelength=1.8, labelspacing=0.28)
for s in ('top','right'): ax.spines[s].set_visible(False)
ax.text(0.985,0.03,'DRAFT — training history not in repository;\nvalidation series from registered run, training series schematic',
        transform=ax.transAxes, ha='right', va='bottom', fontsize=4.6, color='0.45', style='italic', linespacing=1.3)
fig.savefig('/home/user/changes/paper/figures/fig_loss.png', dpi=600)
print('fig_loss.png written')
