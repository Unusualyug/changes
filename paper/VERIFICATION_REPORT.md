# Verification report — MediVision AI manuscript revision

Scope: the repository `Unusualyug/changes` at commit `c738995`. The manuscript
file itself (`.docx`) was **not present** in the repository or in its git history,
so this revision was produced from the code, the committed evaluation artifacts
and the issue list supplied in the review request.

## 1. Artifacts available

| Input | Status |
|---|---|
| `medivision-ai-ml/evaluation_results/evaluation.json` | present — per-finding AUC, precision, recall, F1, sensitivity, specificity, support, confusion matrix; `sample_count` = 830 |
| `medivision-ai-ml/models/metadata.json` | present — architecture, 8 completed epochs, split sizes, metadata spec |
| `evaluation_results/roc_curves.png`, `confusion_matrices.png` | present |
| Image corpus (`data/`) | **absent** — gitignored |
| Trained checkpoint (`models/*.pth`) | **absent** — gitignored |
| Training-loss history | **absent** — not persisted by the training loop |

## 2. What was executed

- Re-derived every metric from the committed confusion counts and compared it with
  the committed JSON (agreement exact for sensitivity, specificity, precision, F1,
  accuracy, macro and micro aggregates).
- Digitised the committed ROC figure on its axis grid and re-integrated the curves:
  Normal 0.7255 vs 0.724, Pneumonia 0.7104 vs 0.709, Pleural effusion 0.8454 vs
  0.844 — agreement within 0.002. **Cardiomegaly 0.9566 vs 0.8054 — a 0.151
  discrepancy that cannot be an extraction artefact** (verified against axis
  calibration, colour assignment and curve occlusion). Most probable cause: the
  figure was produced in a different run from the metrics. Reported in the paper
  (Appendix B) and left visible rather than smoothed over.
- Verified all 25 references against Crossref/DataCite, including the two page
  ranges flagged in the request.
- Implemented and tested the IEEE PDF/DOCX builders, including a QA script that
  scans for placeholders, uncited references and numeric drift.

## 3. Implementation checks requested in the review

| Question | Answer |
|---|---|
| Is `pos_weight = N_neg / N_pos`? | **Yes.** `ml/training/trainer.py` accumulates `pos_counts`/`neg_counts` over the training loader and passes `neg/max(pos,1)` to `BCEWithLogitsLoss`. Caveat recorded in the paper: this cannot improve ROC-AUC (a monotone rescaling does not reorder scores); it only moves the 0.5 operating point. The draft's claim to the contrary was withdrawn. |
| Which augmentations are used? | `RandomAffine(degrees=5, translate=(0.02,0.02), scale=(0.97,1.03))` and `RandomHorizontalFlip(p=0.5)`, training split only. No colour/contrast/gamma/erasing steps. |
| ImageNet mean/SD? | **Yes** — `Normalize([0.485,0.456,0.406], [0.229,0.224,0.225])` in both training and evaluation transforms. |
| Is the 70/15/15 patient-level split overlap-free? | **Yes, by construction.** Splitting is done on unique `Patient ID` with `random_state=42`; images are then filtered by patient. Realised sizes 3,447 / 722 / 830 images (68.95 / 14.44 / 16.60 %). |
| Any other drift? | `numberOfEpochs` in the checkpoint metadata is **8**, not 20 (patience never triggered); the paper now reports both and restricts training discussion to the eight completed epochs. |

## 4. What could not be done, and why

| Requested | Status | Reason / unblock |
|---|---|---|
| Run training + evaluation, fill every placeholder | **Not possible** | No corpus and no checkpoint in the repository; both are gitignored. Every metric in the paper is taken from the committed `evaluation.json` — none is invented. |
| 95% bootstrap CIs per patient | **Not computed** | `ml/evaluation/evaluate.py` writes aggregate metrics + counts only; per-study probabilities and patient IDs are discarded. Fix: persist `(study_id, patient_id, y_true, y_prob)` and resample patients in the eval script. Paper states this and reports no interval. |
| Paired bootstrap ablation | **Not computed; ablation not run** | Requires an image-only checkpoint trained on the identical split, plus paired per-study scores. |
| `fig_gradcam.png` | **Placeholder, labelled** | Needs the trained model and real radiographs. A synthetic map was *not* passed off as model output; the panel is annotated "DRAFT PLACEHOLDER — synthetic composite". |
| `fig_loss.png` | **Validation series real, training series schematic** | Training losses are not persisted. The validation values (0.1595 → 0.1485) are from the registered run; the training curve is drawn offset and labelled schematic in-figure and in the caption. |
| `fig_roc.png` / `fig_confusion.png` | **Produced** | ROC from digitised committed curve coordinates; confusion directly from committed counts. |
| Email with attachments | **Not sent** | Not attempted — see the note in the chat message. |

## 5. Manuscript changes vs. the draft described in the request

- Abstract rewritten to report findings (macro AUC 0.771, per-finding AUCs, macro
  sens/spec/prec/F1, micro F1 0.407) instead of describing the manuscript; the
  bootstrap sentence removed because no interval is computed.
- All `[TBD]` cells replaced by measured values, or by an explicit "not computed"
  status in Table V where the artifacts forbid a value.
- Table I corpus composition, Table II training configuration (as verified in
  code), Table III per-finding metrics, Table IV confusion counts, Table V
  statistical-analysis status, Table VI claim-to-implementation matrix, Table VII
  bibliography corrections.
- Related work extended to label noise, shortcut learning, calibration, subgroup
  bias, multimodal fusion and saliency limits, plus an explicit Evaluation
  Protocol subsection.
- Discussion adds the PA/AP shortcut argument, a metadata-only control proposal
  and a counterfactual permutation audit.
- Limitations rewritten as eleven scope conditions.
- 25 references, every one cited, each resolved against a registry record. Two
  page ranges corrected (ChestX-ray8 → 3462–3471; DenseNet → 2261–2269) and the
  non-resolving CheXpert CVPR DOI replaced by the AAAI record.

## 6. Before submission

1. Re-run evaluation from the current checkpoint so figure, Table III and Table IV
   are provably from one pass (resolves the Cardiomegaly curve discrepancy).
2. Persist per-study predictions, then add 95% patient-level bootstrap CIs and the
   paired ablation; restore the corresponding sentences.
3. Register an image-only and a metadata-only control checkpoint.
4. Replace the two placeholder figures.
5. Run the metadata-permutation audit described in Section V-C.
