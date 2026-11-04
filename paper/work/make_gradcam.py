import json, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib import rcParams
import matplotlib.patches as mpatches
rcParams.update({'font.family':'serif','font.serif':['DejaVu Serif'],'font.size':8,
 'axes.labelsize':8,'axes.titlesize':8.2,'xtick.labelsize':6,'ytick.labelsize':6,
 'axes.linewidth':0.6,'figure.dpi':600,'savefig.bbox':'tight','savefig.pad_inches':0.03})
res=json.load(open('results.json')); pc=res['per_class']
order=[('Normal','Normal'),('Pneumonia','Pneumonia'),('Cardiomegaly','Cardiomegaly'),('Pleural_Effusion','Pleural effusion')]
rng=np.random.default_rng(7)
H,W=224,224
yy,xx=np.mgrid[0:H,0:W]
def lung_mask():
    left=((xx-78)/40.0)**2+((yy-116)/86.0)**2<1
    right=((xx-146)/40.0)**2+((yy-116)/86.0)**2<1
    return (left|right)
thorax=((xx-112)/92.0)**2+((yy-112)/104.0)**2<1
bg=np.clip(0.10+0.05*rng.standard_normal((H,W)),0,1)
img=bg.copy(); lm=lung_mask(); img[lm]=np.clip(0.42+0.09*rng.standard_normal(lm.sum()),0,1)
img[~thorax]=np.clip(img[~thorax]*0.55,0,1)
from scipy.ndimage import gaussian_filter
cams={}
spots={'Normal':[(78,96,30),(146,96,30),(112,180,26)],
       'Pneumonia':[(70,150,34)],
       'Cardiomegaly':[(112,132,52)],
       'Pleural_Effusion':[(60,196,30),(166,196,30)]}
for k,pts in spots.items():
    c=np.zeros((H,W))
    for (cx,cy,s) in pts: c+=np.exp(-(((xx-cx)**2+(yy-cy)**2)/(2*s*s)))
    c=gaussian_filter(c,6); c=(c-c.min())/(c.max()-c.min()+1e-9); cams[k]=c

fig,axes=plt.subplots(2,2,figsize=(4.35,3.45))
for ax,(k,label) in zip(axes.ravel(),order):
    ax.imshow(img,cmap='gray',vmin=0,vmax=1)
    ax.imshow(cams[k],cmap='jet',alpha=0.42,vmin=0,vmax=1)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(f"{label} ($p$ = {'0.61' if k=='Normal' else '0.54' if k=='Pneumonia' else '0.58' if k=='Cardiomegaly' else '0.72'})",fontsize=8.0)
    for s in ax.spines.values(): s.set_linewidth(0.5); s.set_color('0.4')
fig.suptitle('DRAFT PLACEHOLDER - synthetic composite, not model output', fontsize=7.2, y=0.015, color='#b03a2e')
fig.tight_layout(rect=(0,0.045,1,1),w_pad=0.8,h_pad=1.1)
fig.savefig('/home/user/changes/paper/figures/fig_gradcam.png', dpi=600)
print('fig_gradcam.png written')
