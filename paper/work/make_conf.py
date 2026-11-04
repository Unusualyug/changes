import json, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams.update({'font.family':'serif','font.serif':['DejaVu Serif'],'font.size':8,
 'axes.labelsize':8.6,'axes.titlesize':8.2,'xtick.labelsize':8.0,'ytick.labelsize':8.0,
 'axes.linewidth':0.7,'figure.dpi':600,'savefig.bbox':'tight','savefig.pad_inches':0.02})
res = json.load(open('results.json')); pc = res['per_class']
NM = {'Normal':'Normal','Pneumonia':'Pneumonia','Cardiomegaly':'Cardiomegaly','Pleural_Effusion':'Pleural effusion'}
order = ['Normal','Pneumonia','Cardiomegaly','Pleural_Effusion']

fig, axes = plt.subplots(2,2, figsize=(4.35,3.75))
for ax,k in zip(axes.ravel(), order):
    d = pc[k]; M = np.array([[d['tn'],d['fp']],[d['fn'],d['tp']]])
    im = ax.imshow(M, cmap='Blues', vmin=0, vmax=M.max()*1.18)
    for i in range(2):
        for j in range(2):
            v = M[i,j]; rel = v/M.sum()*100
            ax.text(j, i, f"{v}\n({rel:.1f}%)", ha='center', va='center',
                    fontsize=8.4, color='white' if v > M.max()*0.55 else '#152238',
                    linespacing=1.25)
    ax.set_xticks([0,1]); ax.set_yticks([0,1])
    ax.set_xticklabels(['Neg.','Pos.']); ax.set_yticklabels(['Neg.','Pos.'])
    ax.set_xlabel('Predicted label'); ax.set_ylabel('True label')
    ax.set_title(f"{NM[k]}\nAUC {d['reported_auc']:.3f}; Sens {d['sens']:.3f}; Spec {d['spec']:.3f}", fontsize=7.9, linespacing=1.25)
    ax.grid(False)
    for s in ax.spines.values(): s.set_linewidth(0.6)
fig.tight_layout(w_pad=1.1, h_pad=1.5)
fig.savefig('/home/user/changes/paper/figures/fig_confusion.png', dpi=600)
print('fig_confusion.png written; n per matrix:', {k:sum(pc[k][x] for x in ('tn','fp','fn','tp')) for k in order})
