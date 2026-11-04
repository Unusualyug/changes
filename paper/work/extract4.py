import numpy as np, json
from PIL import Image
a=np.array(Image.open('/home/user/changes/medivision-ai-ml/evaluation_results/roc_curves.png').convert('RGB')).astype(int)
L,R,B,T=148.5,1128.5,777.5,87.5
COLORS={'Normal':'#1f77b4','Pneumonia':'#ff7f0e','Cardiomegaly':'#2ca02c','Pleural_Effusion':'#d62728'}
grid=np.arange(0,1.0001,0.001); out={}
for name,h in COLORS.items():
    c=np.array([int(h[i:i+2],16) for i in (1,3,5)])
    mask=np.abs(a-c).sum(2)<120
    ys,xs=np.nonzero(mask)
    keep=(xs>=150)&(xs<=1127)&(ys>=88)&(ys<=777)
    xs,ys=xs[keep],ys[keep]
    prof={}
    for x in np.unique(xs):
        prof[x]=ys[xs==x].min()          # topmost pixel per column
    xi=np.array(sorted(prof)); yi=np.array([prof[x] for x in xi])
    Xi=(xi-L)/(R-L); Yi=(B-yi)/(B-T)
    order=np.argsort(Xi); Xi,Yi=Xi[order],Yi[order]
    tpr=np.interp(grid,Xi,Yi,left=Yi[0],right=Yi[-1])
    tpr=np.minimum(np.maximum.accumulate(tpr),1.0)
    out[name]={'fpr':grid.tolist(),'tpr':tpr.tolist(),'auc_from_plot':float(np.trapezoid(tpr,grid))}
    print(f"{name:18s} auc_from_plot={out[name]['auc_from_plot']:.4f}  (first x={Xi[0]:.4f}, last x={Xi[-1]:.4f})")
json.dump(out,open('roc_extracted.json','w'))
print("reported:  .7239  .7091  .8054  .8444   macro .7707")
print("macro from plot: %.4f"%np.mean([out[k]['auc_from_plot'] for k in out]))
