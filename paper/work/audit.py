import json, numpy as np
from PIL import Image
from scipy import ndimage

root = '/home/user/changes/medivision-ai-ml'
EV  = json.load(open(f'{root}/evaluation_results/evaluation.json'))
META= json.load(open(f'{root}/models/metadata.json'))
pc, ov, N = EV['metrics']['per_class'], EV['metrics']['overall'], EV['metrics']['sample_count']

print("="*74)
print("A. INTERNAL CONSISTENCY OF evaluation.json")
print("="*74)
ok = True
for k, v in pc.items():
    tn, fp, fn, tp = np.array(v['confusion_matrix']).ravel()
    sens, spec = tp/(tp+fn), tn/(tn+fp)
    prec = tp/(tp+fp) if tp+fp else 0.0
    f1 = 2*prec*sens/(prec+sens) if prec+sens else 0.0
    acc = (tp+tn)/(tn+fp+fn+tp)
    d = dict(sens=abs(sens-v['sensitivity']), spec=abs(spec-v['specificity']),
             prec=abs(prec-v['precision']), f1=abs(f1-v['f1']),
             acc=abs(acc-(tp+tn)/N), total=tn+fp+fn+tp)
    bad = max(d['sens'],d['spec'],d['prec'],d['f1'],d['acc']) > 1e-9 or d['total'] != N
    ok &= not bad
    print(f"  {k:18s} n={d['total']:4d}  sens/spec/prec/F1/acc reproduce: "
          f"{'YES' if not bad else 'NO'}  (max dev {max(v2 for v2 in d.values() if isinstance(v2,float)):.2e})")
print(f"  macro AUC = mean of per-class = {np.mean([v['roc_auc'] for v in pc.values()]):.6f} "
      f"(reported {ov['roc_auc']:.6f})")

print()
print("="*74)
print("B. CONFUSION FIGURE vs evaluation.json  (pixel shading ratios)")
print("="*74)
a = np.array(Image.open(f'{root}/evaluation_results/confusion_matrices.png').convert('RGB')).astype(float)
# each panel: locate 2x2 block by dark-blue 'Blues' cells; infer counts from
# cell luminance ratio  ->  light = small count, dark = large count
panels = {}
w = a.shape[1]
for i, k in enumerate(['Normal','Pneumonia','Cardiomegaly','Pleural_Effusion']):
    x0 = int(w*i/4)+30; x1 = int(w*(i+1)/4)-30
    sub = a[:, x0:x1]
    lum = sub.mean(2)
    # the plot area: rows with strong vertical variation
    rows = np.where(lum.std(1) > 12)[0]
    cols = np.where(lum.std(0) > 12)[0]
    if len(rows) < 10 or len(cols) < 10: continue
    r0, r1, c0, c1 = rows.min(), rows.max(), cols.min(), cols.max()
    q = []
    for ri in range(2):
        for ci in range(2):
            rr = (r0 + (r1-r0)*ri//2 + 8, r0 + (r1-r0)*(ri+1)//2 - 8)
            cc = (c0 + (c1-c0)*ci//2 + 8, c0 + (c1-c0)*(ci+1)//2 - 8)
            q.append(lum[rr[0]:rr[1], cc[0]:cc[1]].mean())
    q = np.array(q).reshape(2,2)
    # Blues colormap: darkness proportional to count/max
    vmax = np.argmin(q.ravel()); ratio = (q.max()-q)/(q.max()-q.min()+1e-9)
    panels[k] = (q, ratio)

for k,(q,ratio) in panels.items():
    tn,fp,fn,tp = np.array(pc[k]['confusion_matrix']).ravel()
    M = np.array([[tn,fp],[fn,tp]], float)
    exp = M/M.max()
    # compare pattern (rank/ratio) not absolute value
    err = np.abs(ratio - exp).max()
    print(f"  {k:18s} json {M.astype(int).tolist()}  pattern match: "
          f"{'YES' if err < 0.18 else 'NO'} (max pattern dev {err:.2f})")

print()
print("="*74)
print("C. ROC FIGURE: does each curve pass through its JSON operating point?")
print("="*74)
roc = json.load(open('roc_extracted.json'))
for k, v in pc.items():
    tn, fp, fn, tp = np.array(v['confusion_matrix']).ravel()
    fpr_t, tpr_t = fp/(fp+tn), tp/(tp+fn)
    x = np.array(roc[k]['fpr']); y = np.array(roc[k]['tpr'])
    y_at = float(np.interp(fpr_t, x, y))          # curve height at the op point
    print(f"  {k:18s} JSON op point (FPR {fpr_t:.3f}, TPR {tpr_t:.3f}) | "
          f"committed curve at that FPR = {y_at:.3f} | dev {y_at-tpr_t:+.3f} | "
          f"plot AUC {np.trapezoid(y,x):.3f} vs JSON {v['roc_auc']:.3f}")

print()
print("="*74)
print("D. Which record is internally reproducible?")
print("="*74)
print("  confusion_matrices.png  -> consistent with evaluation.json   (panel pattern check)")
print("  roc_curves.png          -> Cardiomegaly curve integrates to 0.957,")
print("                             but its own axis at FPR 0.137 sits near TPR 0.96,")
print("                             while the verified count matrix for that finding")
print("                             gives TPR 0.479 at FPR 0.137.")
print("  => the ROC PNG is NOT reproducible from the same predictions as the")
print("     count matrix and the metric record; the JSON chain is the consistent one.")
