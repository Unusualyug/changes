import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib import rcParams
rcParams.update({'font.family':'serif','font.serif':['DejaVu Serif'],'figure.dpi':600,
 'savefig.bbox':'tight','savefig.pad_inches':0.05})
fig,ax=plt.subplots(figsize=(7.0,2.9)); ax.set_xlim(0,100); ax.set_ylim(-1,42); ax.axis('off')
def box(x,y,w,h,t,fc,fs=6.0):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.45,rounding_size=1.0",
                 linewidth=0.8,edgecolor='#1f3350',facecolor=fc))
    ax.text(x+w/2,y+h/2,t,ha='center',va='center',fontsize=fs,color='#10203a',linespacing=1.4)
def arr(p1,p2,rad=0.0):
    ax.add_patch(FancyArrowPatch(p1,p2,arrowstyle='-|>',mutation_scale=6.5,linewidth=0.75,
                 color='#1f3350',shrinkA=2,shrinkB=2,connectionstyle=f"arc3,rad={rad}"))
R1,R2,R3=31,17,3; H=7.5
box(0.5,R1,18.5,H,'NIH ChestX-ray14\n4,999-image subset\nreport-derived labels','#e8eef7')
box(22,R1,17,H,'Patient-level split\n70 / 15 / 15 (seed 42)','#e8eef7')
box(42,R1,18,H,'Pre-processing\n224x224 RGB\nImageNet statistics','#e8eef7')
box(63,R1,17,H,'Augmentation\naffine 5 deg, flip 0.5\nscale 0.97-1.03','#e8eef7')
box(83,R1,16.5,H,'Metadata vector\n11-d (age, sex, view,\nsize, pixel spacing)','#f3ece0')
box(0.5,R2,24,H,'DenseNet121 backbone\nImageNet-initialised\n1,024-d pooled features','#dfeee6')
box(29,R2,22,H,'Metadata encoder\n11-32-ReLU-BN-Dropout\n32-d embedding','#f3ece0')
box(55,R2,20,H,'Fusion and head\ncat(1024,32)-Dropout-\nLinear(1056,4) logits','#dfeee6')
box(0.5,R3,22,H,'Weighted BCE objective\npos_weight = N$_{neg}$/N$_{pos}$\nper finding','#f7e6e2')
box(27,R3,22,H,'Held-out evaluation\nn = 830, threshold 0.50\ncounts + metrics stored','#f7e6e2')
box(53.5,R3,18,H,'Grad-CAM\nqualitative attention\n(research aid)','#f7e6e2')
box(76,R3,23.5,H,'Not stored: per-study scores,\ncurve coordinates, loss history\n(bootstrap CIs blocked)','#efe7f3',5.6)
for x1,x2 in [(19,22),(39,42),(60,63),(80,83)]: arr((x1,R1+H/2),(x2,R1+H/2))
arr((91,R1),(90,R2+H+0.6),0.0)
arr((66,R1),(14,R2+H+0.6),-0.05)
arr((24.5,R2+H/2),(29,R2+H/2)); arr((51,R2+H/2),(55,R2+H/2))
arr((62,R2),(45,R3+H+0.6)); arr((62,R2),(13,R3+H+0.6)); arr((70,R2),(63,R3+H+0.6))
ax.text(0,40.3,'Stage 1 - data assembly, splitting and augmentation',ha='left',fontsize=5.9,color='0.40',style='italic')
ax.text(0,26.0,'Stage 2 - multimodal encoder and fusion',ha='left',fontsize=5.9,color='0.40',style='italic')
ax.text(0,12.2,'Stage 3 - objective, evaluation and interpretation',ha='left',fontsize=5.9,color='0.40',style='italic')
fig.savefig('/home/user/changes/paper/figures/fig_pipeline.png',dpi=600); print('ok')
