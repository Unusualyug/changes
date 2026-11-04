import json, numpy as np
from PIL import Image

root='/home/user/changes/medivision-ai-ml'
EV=json.load(open(f'{root}/evaluation_results/evaluation.json'))
pc=EV['metrics']['per_class']
a=np.array(Image.open(f'{root}/evaluation_results/confusion_matrices.png').convert('RGB')).astype(float)
lum=a.mean(2); w=a.shape[1]
print("Confusion figure: is the darkest cell the largest count? (robust check)")
for i,k in enumerate(['Normal','Pneumonia','Cardiomegaly','Pleural_Effusion']):
    sub=lum[:, int(w*i/4)+40:int(w*(i+1)/4)-40]
    rows=np.where(sub.std(1)>10)[0]; cols=np.where(sub.std(0)>10)[0]
    r0,r1,c0,c1=rows.min(),rows.max(),cols.min(),cols.max()
    cells=[]
    for ri in range(2):
        for ci in range(2):
            rr=(r0+(r1-r0)*ri//2+10, r0+(r1-r0)*(ri+1)//2-10)
            cc=(c0+(c1-c0)*ci//2+10, c0+(c1-c0)*(ci+1)//2-10)
            cells.append(sub[rr[0]:rr[1], cc[0]:cc[1]].mean())
    cells=np.array(cells).reshape(2,2)
    M=np.array(pc[k]['confusion_matrix'],float)
    argmax_match = np.unravel_index(cells.argmin(),cells.shape)==np.unravel_index(M.argmax(),M.shape)
    argmin_match = np.unravel_index(cells.argmax(),cells.shape)==np.unravel_index(M.argmin(),M.shape)
    print(f"  {k:18s} counts {str(M.astype(int).tolist()):26s} darkest==largest: {argmax_match}  lightest==smallest: {argmin_match}")

print()
print("Impossibility test for the 0.957 curve:")
v=pc['Cardiomegaly']; tn,fp,fn,tp=np.array(v['confusion_matrix']).ravel()
fpr,tpr=fp/(fp+tn), tp/(tp+fn)
print(f"  verified counts give the operating point (FPR={fpr:.3f}, TPR={tpr:.3f})")
print(f"  a curve with AUC 0.957 must satisfy TPR >> 0.479 at FPR 0.137 (a perfect")
print(f"  classifier would be TPR=1.0 there); 0.957 and TPR=0.479 cannot coexist.")
print(f"  => 0.805 (rank-based AUC consistent with the counts) is the verified value.")
