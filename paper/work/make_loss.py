import json, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams.update({'font.family':'serif','font.serif':['DejaVu Serif'],'font.size':8,
 'axes.labelsize':8,'axes.titlesize':8,'xtick.labelsize':7,'ytick.labelsize':7,
 'axes.linewidth':0.7,'figure.dpi':600,'savefig.bbox':'tight','savefig.pad_inches':0.02})
res=json.load(open('results.json'))

fig,ax=plt.subplots(figsize=(4.35,1.55))
ax.set_xlim(1,8); ax.set_ylim(0,0.20)
ax.set_xlabel('Epoch'); ax.set_ylabel('Weighted BCE loss')
ax.set_xticks(range(1,9))
for s in ('top','right'): ax.spines[s].set_visible(False)
msg = ('Training and validation loss curves unavailable\n'
       'The training loop does not persist the loss series and the\n'
       'released checkpoint carries no history object.\n'
       'No value is reconstructed or estimated here.')
ax.text(0.5,0.53,msg,transform=ax.transAxes,ha='center',va='center',fontsize=7.4,
        linespacing=1.65,color='#8a1c12')
ax.plot([],[],alpha=0)
fig.savefig('/home/user/changes/paper/figures/fig_loss.png', dpi=600)
print('fig_loss.png written (explicit no-data panel)')
