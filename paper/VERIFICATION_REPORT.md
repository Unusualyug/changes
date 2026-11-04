# Verification Report — MediVision AI manuscript

**Revision 3.** Supersedes revision 2. Documents what was verified, what was
changed in response to external review, what is still not verifiable, and why.

Artifacts: `MediVision_AI_IEEE_Research_Final.pdf` (14 pp.), `.docx`,
`figures/` (3 figures at 600 dpi), `work/stats.json` (every derived number).

---

## 1. What changed in revision 3, and why

### 1.1 The AUC bracket in Fig. 2(b) was wrong — corrected

Revision 2 claimed that "the trapezoidal brackets implied by the operating
point are 0.536 and 0.707, which enclose 0.805 but exclude 0.957." **That
sentence contradicted itself**: 0.805 > 0.707. The numbers came from an invalid
construction (half the unit square instead of a bound on the area), not from a
theorem.

The correct statement is a closed-form bound. A ROC curve is non-decreasing from
(0,0) to (1,1) and passes through the verified operating point (f, t). Its area
is therefore at least the area under the piecewise-linear path through that
point, and at most the area of the path that rises to TPR = 1 before the point
and stays there:

    A_min = ½·f·t + (1−f)·t        A_max = f·t + (1−f)

Both bounds are attainable, so the interval is exact for a single operating
point. For Cardiomegaly, f = 104/757 = 0.1374 and t = 35/73 = 0.4795:

    A_min = 0.4465        A_max = 0.9285

The recorded AUC of 0.805 lies inside; a value of 0.957 lies outside. The
review's independent estimate of "about 0.41 to 0.93" is the same bound; the
small difference is the rounding of f and t before substitution. Implemented in
`work/stats.py::auc_bracket`, exercised on all four findings, and reproduced in
the PDF to three decimals.

**The sentence and the numbers now agree**: "A monotone ROC curve through
(0.137, 0.479) has an area between 0.447 and 0.928."

### 1.2 The weighting explanation contradicted the prevalences — removed

Revision 2 said effusion "has the largest positive weight in the training
partition and Cardiomegaly among the smallest." This is incoherent: with
w = N_neg/N_pos, the *rarer* finding gets the *larger* weight, and Cardiomegaly
(8.8%) is rarer than effusion (13.6%). Since training-partition prevalences are
not in the release, the claim was unverifiable as well as wrong.

It is deleted. What remains is the analytically correct statement: the weight is
largest where a finding is rarest, so the fixed 0.50 threshold lands at very
different positions across findings, and the individual weights cannot be quoted
because the training positive counts are not retained.

### 1.3 Title and abstract

Title: "A **Reproducible** Multimodal DenseNet121 Framework …" → "A Multimodal
DenseNet121 **Baseline** … with an Audit of What Its Evaluation Record Can and
Cannot Support". "Reproducible" is dropped because the evaluation cannot be
re-executed from the release (no checkpoint, no corpus). Abstract is cut from
~460 words to 233 and no longer claims a fusion benefit.

### 1.4 Placeholder and no-data figures — deleted

| Revision 2 | Revision 3 |
|---|---|
| `fig_gradcam.png`, captioned "synthetic layout placeholder" | **deleted**; §V-F states no saliency map is shown and why |
| `fig_loss.png`, an empty "no data" panel | **deleted**; §IV-B states in one sentence that no loss series survives |
| `fig_roc.png` (a) curves digitised from the archived PNG | **redrawn** as verified operating points only — no curve is drawn, because aggregate counts do not determine the interior of a ROC curve |
| `fig_roc.png` (b) "constraint diagram" | **redrawn** as recorded AUC with 95% Hanley–McNeil intervals and attainable ranges |

No figure in the paper is now synthetic, illustrative, or a placeholder.

### 1.5 Intervals are now reported (they were wrongly declared impossible)

Revision 2's Table V said "no confidence interval for sensitivity or
specificity can be computed." That was false: Clopper–Pearson intervals follow
directly from TP/FN/TN/FP. Revision 3 adds two constructions that need only
counts (`work/stats.py`):

* exact binomial (Clopper–Pearson) intervals for every sensitivity and
  specificity, cross-checked against Wilson;
* Hanley–McNeil normal-approximation intervals for every AUC (Eq. 6).

The Pneumonia row now shows the point vividly: sensitivity 0.667 with a 95%
interval of **0.22–0.96** on six positives.

Still unavailable, and still stated as such: anything requiring pairing or
resampling — intervals on macro averages, subgroup strata, calibration, and any
model-to-model comparison.

### 1.6 Macro averages restated

The all-finding macro AUC (0.771) gives a sixth of its weight to a six-event
finding, and the paper now says so. A second macro average over the three
findings with ≥30 positives (Normal, Cardiomegaly, Pleural effusion) is reported
alongside: **AUC 0.791, sensitivity 0.628, specificity 0.767**. The
three-finding average is designated the interpretable summary.

### 1.7 Structure and writing

* The paper no longer reads as a revision log: "the earlier draft credited …",
  "must not claim …", "the original review request", "the manuscript and code had
  drifted apart" are all gone. The claim-to-implementation table now states
  results, not corrections.
* The Cardiomegaly discrepancy is argued **once**, in §IV-G (three paragraphs).
  It previously appeared in ten places.
* §II-H (evaluation protocol) moved into Methods (§III-G, *Evaluation Metrics and
  Intervals*). Related Work is now only related work.
* The verification section is no longer numbered after the Conclusion; it is an
  Appendix.
* Ethics and data/code availability statements added (Declarations).
* Fixed: "Fig. Fig.", "Table I" announced before it appeared, F-item ordering,
  the conclusion's "three findings" that listed four with two "Second"s, and the
  conclusion mis-attributing F4 instead of F6.
* Every table and figure reference is now an auto-resolved cross-reference, and
  a checker confirms no float is cited before it appears and no number is skipped.

### 1.8 Claims removed

| Claim | Status |
|---|---|
| "evaluation retains enough for bootstrap CIs and an ablation" | contradicted by the record; removed |
| "metadata fusion contributes" | unevidenced (no control model); removed |
| "reproducible" | not satisfied by the release; removed from title and abstract |
| "best validation loss occurred at the final epoch" | not recorded anywhere; removed |
| validation-loss figures 0.1595 → 0.1485 | removed in revision 2, remains removed |

---

## 2. What is verified, and how

`work/stats.py` reads `medivision-ai-ml/evaluation_results/evaluation.json` and
computes every derived quantity; `work/stats.json` is its output. The manuscript
imports those values (`content.py` reads `stats.json` at build time), so no
number in the tables is typed by hand.

Checks that pass on the built PDF and DOCX:

1. **Arithmetic closure.** All twenty stored metrics reproduce from the stored
   count matrices to ≤ 6 × 10⁻¹⁷; every matrix sums to 830; the stored macro AUC
   equals the mean of the four per-finding AUCs.
2. **Figure/record agreement.** The confusion figure's cell shading ranks agree
   with the count matrices for all four findings.
3. **Operating-point test.** Each finding's count matrix fixes one (FPR, TPR).
   Three archived curves pass through their own operating point to ≤ 0.004; the
   Cardiomegaly curve misses by 0.480 and is therefore withdrawn from the paper.
4. **Attainable-range test.** Every recorded AUC lies inside the exact range
   implied by its own operating point (Eq. 7). A recorded 0.957 for Cardiomegaly
   would not.
5. **Text/record agreement.** Every interval printed in the PDF appears verbatim
   in `stats.json` (checked programmatically, 0 mismatches).
6. **Reference integrity.** All 25 entries cited at least once, all present in
   the bibliography, all resolved against Crossref/DataCite.
7. **No placeholders.** No `[TBD]`, markup residue, highlight, TODO or
   placeholder caption in either output.

---

## 3. What could not be done, and the one thing that blocks closure

The review's first and most important point stands, and this report should not
soften it: **the results have not been re-derived by re-running the model.**

| Blocked action | Reason | Consequence |
|---|---|---|
| Re-run evaluation on the 830-study partition | `models/best_model.pth` and `data/` are excluded from version control and absent from the repository | 0.805 remains the *recorded* value; the ROC panel cannot be regenerated |
| Persist per-study predictions | Requires the re-run above | no bootstrap intervals, no subgroup table, no calibration |
| Image-only / metadata-only ablation | Requires retraining from the corpus | no fusion claim is made anywhere in the paper |
| Metadata permutation audit | Requires the checkpoint and test images | recorded as specified-but-not-run (§IV-F) |
| Real Grad-CAM maps | Requires the checkpoint and radiographs | figure deleted rather than approximated |

The code already emits everything needed except the predictions; the change is
one block in `ml/evaluation/evaluate.py` (write `y_true`, `probs`,
`patient_ids`, and the FPR/TPR arrays into the JSON record). With the corpus and
checkpoint restored, the closure procedure is:

1. run `python -m ml.evaluation.evaluate …`;
2. accept the run only if all four tests in §2 pass (closure, figure agreement,
   operating point ≤ 0.01, curve integral within 0.01 of the reported AUC);
3. rebuild tables and figures from the new record — no manual editing;
4. then, and only then, add bootstrap intervals and the ablation.

---

## 4. Honest statement of the paper's standing

With the corrections in this revision the manuscript is internally consistent,
every reported number is reproducible from the released metric record, and no
figure is synthetic. It is **not** a strong empirical result: the cohort is
4,999 images, four of fourteen findings are modelled, one seed was run, training
stopped at 8 of 20 epochs, one finding has six positives, and there is no
baseline model of any kind. The paper now says all of this in its own voice,
in the abstract as well as the limitations section, and claims no fusion benefit
and no clinical utility.
