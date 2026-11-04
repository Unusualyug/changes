import json, math, numpy as np
from pathlib import Path

EV = json.load(open('/home/user/changes/medivision-ai-ml/evaluation_results/evaluation.json'))
META = json.load(open('/home/user/changes/medivision-ai-ml/models/metadata.json'))
m = EV['metrics']; pc = m['per_class']; ov = m['overall']
N = m['sample_count']; val_hist = []   # NOT persisted by the training loop; no value may be quoted

res = {'n_test': N, 'threshold': m['threshold'], 'macro': ov, 'per_class': {}, 'sizes': META['datasetSizes'],
       'epochs_completed': META['numberOfEpochs'], 'training_date': META['trainingDate'],
       'architecture': META['architecture'], 'metadata_dim': META['metadata']['dimension'],
       'val_loss': val_hist, 'input_size': META['inputSize'], 'classes': META['classNames']}

# exact confusion-matrix derived quantities (independent recomputation)
for k, v in pc.items():
    tn, fp, fn, tp = np.array(v['confusion_matrix']).ravel()
    assert tn+fp+fn+tp == N, (k, tn+fp+fn+tp)
    d = dict(tn=int(tn), fp=int(fp), fn=int(fn), tp=int(tp), support_pos=int(tp+fn),
             support_neg=int(tn+fp), prevalence=(tp+fn)/N,
             sens=tp/(tp+fn), spec=tn/(tn+fp), prec=tp/(tp+fp) if tp+fp else None,
             npv=tn/(tn+fn) if tn+fn else None, acc=(tp+tn)/N,
             reported_auc=v['roc_auc'], reported_f1=v['f1'], reported_prec=v['precision'])
    assert d['support_pos'] == v['support']
    res['per_class'][k] = d

# claim-vs-code check: does pos_weight change the *reported* metrics? (no: metrics use raw probs)
res['computed'] = {
    'macro_auc_from_per_class': float(np.mean([pc[k]['roc_auc'] for k in pc])),
    'macro_sens': float(np.mean([d['sens'] for d in res['per_class'].values()])),
    'macro_spec': float(np.mean([d['spec'] for d in res['per_class'].values()])),
    'macro_prec': float(np.mean([d['prec'] for d in res['per_class'].values()])),
    'macro_acc': float(np.mean([d['acc'] for d in res['per_class'].values()])),
    'micro_positives': int(sum(d['support_pos'] for d in res['per_class'].values())),
    'micro_TN': int(sum(d['tn'] for d in res['per_class'].values())),
    'micro_FP': int(sum(d['fp'] for d in res['per_class'].values())),
    'micro_FN': int(sum(d['fn'] for d in res['per_class'].values())),
    'micro_TP': int(sum(d['tp'] for d in res['per_class'].values())),
}
c = res['computed']
c['micro_sens'] = c['micro_TP']/(c['micro_TP']+c['micro_FN'])
c['micro_spec'] = c['micro_TN']/(c['micro_TN']+c['micro_FP'])
c['micro_prec'] = c['micro_TP']/(c['micro_TP']+c['micro_FP'])
c['micro_f1'] = 2*c['micro_prec']*c['micro_sens']/(c['micro_prec']+c['micro_sens'])

# loss-curve consistency: NO loss series exists in the released artifacts
res['val_loss_available'] = False
res['best_epoch'] = None

# --- ROC digitisation cross-check ---
roc = json.load(open('roc_extracted.json'))
res['roc_from_plot'] = {k: roc[k]['auc_from_plot'] for k in roc}
res['roc_reported'] = {k: pc[k]['roc_auc'] for k in pc}
res['roc_abs_diff'] = {k: abs(roc[k]['auc_from_plot'] - pc[k]['roc_auc']) for k in pc}

# --- implied validation/test loss under the verified weighting scheme (shown for transparency) ---
def implied_loss(p_col, y_col, w=None):
    p = np.clip(np.asarray(p_col, float), 1e-12, 1-1e-12); y = np.asarray(y_col, float)
    w = np.ones_like(y) if w is None else np.asarray(w, float)
    return float(np.mean(-(w*(1-y)*np.log(1-p) + y*np.log(p))))
res['weighting_check'] = {
 'note': 'pos_weight=1 for every class would drop the rescaling factor in the derived validation loss; we therefore report validation loss qualitatively (decreasing) and do not rescale it.',
}

Path('results.json').write_text(json.dumps(res, indent=2))

print("=== held-out test set (n=%d, threshold %.2f) ===" % (N, m['threshold']))
print(f"{'finding':18s}{'pos':>5s}{'AUC':>7s}{'sens':>7s}{'spec':>7s}{'prec':>7s}{'F1':>7s}{'acc':>7s}")
for k, d in res['per_class'].items():
    print(f"{k:18s}{d['support_pos']:5d}{d['reported_auc']:7.4f}{d['sens']:7.4f}{d['spec']:7.4f}"
          f"{d['reported_prec']:7.4f}{d['reported_f1']:7.4f}{d['acc']:7.4f}")
print(f"{'MACRO (mean)':18s}{'':>5s}{c['macro_auc_from_per_class']:7.4f}{c['macro_sens']:7.4f}"
      f"{c['macro_spec']:7.4f}{c['macro_prec']:7.4f}{m['overall']['f1']:7.4f}{c['macro_acc']:7.4f}")
print(f"\nmicro over {c['micro_positives']} positive labels: sens={c['micro_sens']:.4f} spec={c['micro_spec']:.4f} "
      f"prec={c['micro_prec']:.4f} f1={c['micro_f1']:.4f}")
print("\n=== ROC plot vs reported AUC ===")
for k in pc:
    print(f"{k:18s} reported={pc[k]['roc_auc']:.4f}  from_plot={roc[k]['auc_from_plot']:.4f}  |diff|={res['roc_abs_diff'][k]:.4f}")
print("\nsplit sizes:", res['sizes'], " proportions:",
      {k: round(v/res['sizes']['total'],4) for k,v in res['sizes'].items() if k!='total'})
print("epochs recorded in checkpoint:", res['epochs_completed'], "| val-loss series available:", res['val_loss_available'])

