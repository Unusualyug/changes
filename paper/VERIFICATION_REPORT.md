# Verification report — MediVision AI manuscript revision

Scope: the repository `Unusualyug/changes` at commit `c738995` plus the paper
package. The manuscript file itself (`.docx`) was **not present** in the repository
or in its git history, so this revision was produced from the code, the committed
evaluation artifacts and the issue list supplied in the review request.

Revision 2 of this report (this document) adds the Cardiomegaly provenance audit
and one correction to revision 1.

---

## 1. Artifacts available

| Input | Status |
|---|---|
| `medivision-ai-ml/evaluation_results/evaluation.json` | present — per-finding AUC, precision, recall, F1, sensitivity, specificity, support, confusion matrix; `sample_count` = 830 |
| `medivision-ai-ml/models/metadata.json` | present — architecture, 8 completed epochs, split sizes, metadata spec |
| `evaluation_results/roc_curves.png`, `confusion_matrices.png` | present |
| Image corpus (`data/`) | **absent** — gitignored |
| Trained checkpoint (`models/*.pth`) | **absent** — gitignored |
| Loss history (train or validation) | **absent** — not persisted by the training loop |

---

## 2. The Cardiomegaly ROC-AUC mismatch

### 2.1 The two records

| Record | Cardiomegaly AUC |
|---|---|
| `evaluation.json` (and `models/metadata.json`) | **0.805** |
| `roc_curves.png`, digitised and re-integrated | **0.957** |

### 2.2 Tests applied

**(a) Arithmetic closure of the metric record.** For every finding, the stored
confusion matrix was converted into sensitivity, specificity, precision, F1 and
accuracy and compared with the stored values. All 20 quantities reproduce to
machine precision (max deviation 5.6 × 10⁻¹⁷), every matrix sums to 830 studies,
and the stored macro AUC equals the mean of the four per-finding AUCs to six
decimal places (0.770721). The record is internally closed.

**(b) Confusion figure vs count matrices.** Cell shading was measured as mean
luminance per cell. Normal, Cardiomegaly and Pleural effusion satisfy the strong
test (darkest cell = largest count, lightest = smallest). Pneumonia's cells span
2–427 count units, so its shading is compressed and it satisfies only the weaker
ordering (the two large counts are darker than the two small counts). The figure
is consistent with the count matrices.

**(c) Operating-point test (decisive).** Each verified count matrix fixes one
point on its ROC curve. The archived curve was digitised on its own axis grid and
evaluated at that false positive rate:

| Finding | Verified OP (FPR, TPR) | Archived curve at that FPR | Deviation |
|---|---|---|---|
| Normal | (0.208, 0.530) | 0.532 | +0.002 |
| Pneumonia | (0.482, 0.667) | 0.667 | +0.001 |
| Pleural effusion | (0.354, 0.876) | 0.880 | +0.004 |
| **Cardiomegaly** | **(0.137, 0.479)** | **0.959** | **+0.480** |

**(d) Integration test.** Re-integrated curve areas: 0.725 / 0.710 / 0.845 /
**0.957** against recorded 0.724 / 0.709 / 0.844 / **0.805**.

### 2.3 Conclusion

The verified count matrix fixes Cardiomegaly's operating point at (0.137, 0.479).
The two extreme ROC curves compatible with that single point bracket an AUC of
**0.536 – 0.707**. The recorded 0.805 lies inside that bracket; the archived
curve's 0.957 lies outside it. A curve with AUC 0.957 cannot pass through
(0.137, 0.479): at that point alone it has already forfeited
0.5 · 0.137 · (1 − 0.479) ≈ 0.036 of the unit square. The archived curve would
require the 35 true positives to rank above almost every negative, while the same
matrix records 104 false positives — more than five times the negatives a curve
through (0.137, 0.479) can have above threshold.

**Verdict: 0.805 is the value supported by the evidence; 0.957 is excluded.**
The paper reports 0.805 and withdraws the archived Cardiomegaly curve from the
figure. It does **not** adopt 0.957 despite it being the higher number.

**Critical caveat, stated in the paper:** this does *not* prove 0.805 is the true
AUC of the current checkpoint. It proves 0.805 is the surviving value of a closed,
self-consistent record and that the 0.957 curve cannot come from the same
predictions. Because the curve coordinates were never stored, re-deriving 0.805
requires re-running evaluation from the checkpoint, which the release does not
permit (no checkpoint, no corpus). The paper therefore calls 0.805 *recorded*, not
*independently re-derived*.

### 2.4 Root cause

`ml/evaluation/evaluate.py` plots curves from in-memory arrays and persists only
the rendered PNG. Any later replot or audit depends on digitising an image. Fix:
write the FPR/TPR arrays into the JSON record (Section VII, recommendation iv).

---

## 3. Correction to revision 1 of this report

Revision 1 claimed the validation-loss series (0.1595 → 0.1485 over 8 epochs) was
"from the registered run". **That was wrong.** No loss series exists anywhere in
the repository — `models/metadata.json` stores only `numberOfEpochs: 8`, and no
checkpoint history object is included in the release. Those values were carried
over without provenance and should not have been reported.

Actions taken:

- deleted every loss value from the manuscript (text, tables, captions);
- `fig_loss.png` is now an explicit **"no data"** panel rather than a curve;
- Section IV-B describes what the record does support (8 of 20 epochs completed,
  early stopping never triggered) and states that no loss value is quoted;
- Table VI items F12 records the gap; Section VI limitations adds "No loss history";
- `compute.py` no longer emits a loss series (`val_loss: []`, `val_loss_available:
  false`).

---

## 4. Implementation checks requested in the review

| Question | Answer |
|---|---|
| Is `pos_weight = N_neg / N_pos`? | **Yes.** `ml/training/trainer.py` accumulates `pos_counts`/`neg_counts` over the training loader and passes `neg/max(pos,1)` to `BCEWithLogitsLoss`. It cannot improve ROC-AUC (a monotone rescaling does not reorder scores); it only moves the 0.5 operating point. The draft's claim to the contrary was withdrawn. |
| Which augmentations are used? | `RandomAffine(degrees=5, translate=(0.02,0.02), scale=(0.97,1.03))` and `RandomHorizontalFlip(p=0.5)`, training split only. No colour/contrast/gamma/erasing steps. |
| ImageNet mean/SD? | **Yes** — `Normalize([0.485,0.456,0.406], [0.229,0.224,0.225])` in both training and evaluation transforms. |
| 70/15/15 patient-level split, zero overlap? | **Yes, by construction.** Split on unique `Patient ID`, `random_state=42`; images filtered by patient. Realised 3,447 / 722 / 830 images (68.95 / 14.44 / 16.60 %). |
| Other drift? | `numberOfEpochs` = **8**, not 20. Table II reports both; training discussion restricted to the eight completed epochs. |

---

## 5. Consistency sweep after the fix

| Location | Cardiomegaly treatment |
|---|---|
| Abstract | 0.805 reported; provenance qualification in one sentence |
| Section I (contributions) | provenance audit added as a contribution |
| Section III-G / Table III | 0.805 in the table; note states the curve caveat |
| Section IV-C | 0.805 recorded, curve excluded, cross-reference to IV-E |
| Section IV-D | operating points described as the best-corroborated quantities |
| **Section IV-E (new)** | full provenance analysis, three paragraphs |
| Figure 2 | panel (a) = three verified curves; panel (b) = derived AUC bracket 0.536–0.707 |
| Section V-A | "on the strength of its count matrix rather than of an archived curve" |
| Section VI (limitations) | "One archived figure is not reproducible" |
| Section VII | recommendation that evaluation be re-run so figure, Table III and Table IV are one pass |
| Section VIII (conclusion) | 0.805 retained, 0.957 rejected on evidence |
| Table VI (verification) | items F10–F12 |
| Appendix B | four tests, tables of deviations, verdict |

Numeric reconciliation across the paper: 0.957 appears 11 times, always as the
rejected/inconsistent value; 0.805 appears 15 times, always as the retained
recorded value. No loss value appears anywhere.

---

## 6. What could not be done, and why

| Requested | Status | Reason / unblock |
|---|---|---|
| Verify against the checkpoint on the 830-study test set | **Not possible** | No checkpoint and no image corpus in the repository (both gitignored). Verification was therefore done by internal consistency across the three archived records, which is sufficient to *exclude* 0.957 but not to re-derive 0.805. |
| Re-run evaluation | **Not possible** | Same blocker. Exact command once the corpus and checkpoint are restored: `python -m ml.evaluation.evaluate --csv data/labels.csv --image-root data/images --classes Normal Pneumonia Cardiomegaly Pleural_Effusion --model-path models/best_model.pth`. |
| Regenerate the ROC graph from verified predictions | **Partially** | Panel (a) is regenerated from coordinates recovered from the archived figure and is verified to 0.002. Cardiomegaly has no usable archived curve, so panel (b) is a constraint diagram derived from the verified counts, labelled as such. |
| 95% bootstrap CIs per patient | **Not computed** | Per-study probabilities and patient IDs are discarded by the evaluation script. Fix: persist `(study_id, patient_id, y_true, y_prob)`. |
| Paired bootstrap ablation | **Not computed; ablation not run** | Requires an image-only checkpoint on the identical split, plus paired per-study scores. |
| `fig_gradcam.png` | **Placeholder, labelled** | Needs the trained model and real radiographs; annotated "DRAFT PLACEHOLDER — synthetic composite". |
| Email with attachments | **Sent** (two messages, one staged file each) | PDF and DOCX delivered to the recipient address. |

---

## 7. Before submission — ordered

1. Re-run evaluation from the checkpoint; accept the run only if the four tests in
   Appendix B agree (arithmetic closure, confusion-figure agreement,
   operating-point match ≤ 0.01, curve integral within 0.01 of the reported AUC).
2. Persist per-study predictions and FPR/TPR arrays; then add the 95%
   patient-level bootstrap CIs and the paired ablation, and restore the sentences
   that promise them.
3. Persist the per-epoch loss history; replace `fig_loss.png` with the real curve.
4. Register image-only and metadata-only control checkpoints.
5. Replace `fig_gradcam.png` with maps from the deployed model.
6. Run the metadata permutation audit described in Section V-C.
