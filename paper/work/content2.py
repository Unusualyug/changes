# -*- coding: utf-8 -*-
"""Discussion, conclusion, appendix, declarations and the figure registry."""
import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(os.path.join(_HERE, "stats.json")))
PF = S["per_finding"]
AUC = {k: PF[k]["auc"] for k in PF}
MAC = S["macro_all"]
MACR = S["macro_reliable"]
N = S["sample_count"]


def f(x, nd=3):
    return ("%." + str(nd) + "f") % x


FIGURES = {
"pipeline": dict(file="fig_pipeline.png",
  caption="Framework as implemented. Stage 1 assembles the metadata table, partitions it by "
          "patient and builds the augmentation chain; Stage 2 encodes images and metadata "
          "separately and fuses the descriptors; Stage 3 applies the weighted objective, "
          "evaluates at a fixed threshold and produces qualitative explanations. The dashed "
          "box marks the control experiments the release does not contain."),
"roc": dict(file="fig_roc.png",
  caption="Discrimination evidence for the held-out partition (n = " + str(N) + "). "
          "(a) Verified operating points at threshold 0.50, i.e. the single (FPR, TPR) pair "
          "implied by each count matrix. No curve is drawn: aggregate counts do not determine "
          "the interior of a ROC curve, and no curve coordinates were archived. "
          "(b) Recorded AUC per finding (dot), its 95% Hanley-McNeil interval (bar) and the "
          "exact range of AUCs attainable by any monotone curve through the verified operating "
          "point (grey bracket, Eq. 7). The recorded value lies inside its attainable range "
          "for all three findings; the Pneumonia AUC is omitted because its six positive "
          "studies make the interval uninformative."),
"confusion": dict(file="fig_confusion.png",
  caption="Confusion matrices at a fixed threshold of 0.50, one 2 &times; 2 matrix per "
          "finding, with row-normalized percentages. Counts match {tab:T4} exactly. The "
          "Pneumonia matrix should be read with the six-event denominator in mind."),
}

EXTRA_BODY = [
("h1", "V. DISCUSSION AND LIMITATIONS"),
("h2", "A. What the Results Support"),
("p",
 "The results support a narrow and defensible claim: on this subset and this split, a "
 "DenseNet121 plus metadata late-fusion model trained for eight epochs ranks held-out studies "
 "above chance for Pleural effusion (" + f(AUC["Pleural_Effusion"]) + ") and Cardiomegaly ("
 + f(AUC["Cardiomegaly"]) + "), ranks them at a moderate level for Normal ("
 + f(AUC["Normal"]) + "), and does so at a high-sensitivity, low-specificity operating point "
 "for effusion. They do not support a claim of clinical utility, which would require "
 "discrimination against a radiologist-annotated reference, a calibration curve, a "
 "decision-threshold analysis with explicit costs, and evidence of transportability to a "
 "second institution. They also do not support any statement about the contribution of the "
 "metadata channel, for the reason given in Section IV-F."),
("h2", "B. Scale, Covariate Shift and the Size of the Experiment"),
("p",
 "The experiment is small in four respects, and each bounds the interpretation. The cohort is "
 "4,999 images drawn from a corpus of 112,120: less than five percent of the available data, "
 "and with no recorded selection rule. Four of fourteen findings are modeled, so the task is a "
 "projection of the benchmark rather than the benchmark. Training stopped after eight of "
 "twenty epochs, which by the training configuration means the model is under-trained rather "
 "than converged. And one seed was run, so the sensitivity of every number to initialization "
 "and data order is unknown. Finally the corpus is a single-institution collection: images "
 "were acquired on equipment and with protocols that do not represent the range of acquisition "
 "conditions in deployment, and a model validated only internally is expected to be optimistic "
 "relative to that deployment [13]. Covariate shift of this kind is the most likely "
 "explanation for the gap between the AUCs reported here and published ChestX-ray14 results "
 "for the same findings, which are typically obtained on the full corpus with a larger "
 "training budget; the gap is a statement about the experiment, not about the architecture."),
("h2", "C. Clinical Translation: Work, Not Assumption"),
("p",
 "Two things stand between this prototype and any clinical use, and neither is a modelling "
 "detail. The first is evidence cost: a reader study with radiologists, a calibration "
 "analysis, and external validation each require resources comparable to or larger than the "
 "training run itself, and the absence of any of them is a gap in the evidence rather than a "
 "gap in the code. The second is governance: a system that returns finding-level probabilities "
 "for chest radiographs would, in any deployment, be subject to regulatory review, prospective "
 "silent-mode evaluation and a defined route for acting on disagreements with the reporting "
 "radiologist. This paper does neither and claims neither."),
("h2", "D. Label Quality and the Threshold of Evidence"),
("p",
 "The error modes in {tab:T4} are more plausibly attributable to label construction than to "
 "model capacity. A study is labeled Normal when its report contains no positive finding, "
 "which conflates a genuinely normal examination with an under-reported one; a study is "
 "labeled Pneumonia only when the report uses that token, which is rare in a corpus where "
 "pneumonia is typically described descriptively. The asymmetric noise regime described by "
 "Karimi et al. [14] therefore applies: the positive class is comparatively clean, the "
 "negative class is contaminated, and the classifier is pushed toward over-prediction, which "
 "is the pattern of " + str(PF["Normal"]["counts"]["fn"]) + " Normal false negatives and "
 + str(PF["Pleural_Effusion"]["counts"]["fp"]) + " effusion false positives. This reading is "
 "an argument, not a measurement: no radiologist-annotated subset was used to estimate the "
 "noise rate. Under the argument, the largest available improvement is annotational rather "
 "than architectural, but the paper does not claim to have demonstrated that."),
("h2", "E. The Fixed Threshold and the Missing Operating-Point Analysis"),
("p",
 "The fixed threshold of 0.50 is appropriate for an evaluation protocol, because it prevents "
 "the test set from being used to select an operating point, but it is not a clinical decision "
 "rule. With positive weighting the implicit prior differs across findings, so a single "
 "threshold places four decision boundaries at inconsistent positions on their ROC curves, as "
 "{tab:T3} shows. A deployment would require per-finding thresholds selected on validation "
 "data against explicit costs; the validation partition exists, was used for checkpoint "
 "selection, and was not used for this. Precision-recall curves, which summarize performance "
 "better than ROC at these prevalences, were not produced, and their absence is a gap that "
 "the retained artifacts cannot close without re-running evaluation."),
("h2", "F. Calibration, Subgroups and Explanations"),
("p",
 "No calibration analysis is reported. The weighted objective deliberately distorts predicted "
 "probabilities relative to empirical frequencies, so outputs must not be interpreted as risk "
 "[15]. On subgroup behaviour, the framework ingests age and sex as features and reports no "
 "stratified metrics; given the documented underdiagnosis bias of chest radiograph classifiers "
 "in under-served populations [16] and the gender-imbalance effects reported by Larrazabal et "
 "al. [17], the absence of a subgroup table is a substantive gap. Grad-CAM maps are produced "
 "by the service for qualitative inspection but are not shown here: the release contains "
 "neither radiographs nor a checkpoint, the framework includes no saliency sanity check, and "
 "post-hoc explanations should not carry the evidentiary weight of an interpretable model "
 "design [11]. A synthetic or illustrative saliency panel would be indistinguishable from "
 "fabricated evidence, so the paper omits the figure rather than approximating it."),
("h2", "G. Limitations"),
("p",
 "The following are stated as scope conditions, not as future work."),
("bullets", [
 "<b>Single-corpus internal validation.</b> All reported numbers come from one institution's "
 "corpus and one patient-disjoint split. No external cohort, no cross-institution transport "
 "test and no temporal validation are reported, so the figures should be expected to be "
 "optimistic relative to deployment [13].",
 "<b>No bootstrap intervals and no paired comparison.</b> Patient-level bootstrap intervals "
 "and the paired ablation called for by the protocol could not be computed because per-study "
 "predictions were not retained; exact binomial and Hanley-McNeil intervals are reported "
 "instead, and they ignore within-patient clustering. Consequently no difference between this "
 "model and any other system, including its own ablation, is reported as statistically "
 "supported.",
 "<b>No control models.</b> No image-only model, no metadata-only model and no alternative "
 "backbone were trained. The study therefore contains no baseline, no ablation and no "
 "comparison with published results; the architecture's behaviour relative to any of these is "
 "unknown.",
 "<b>Small-event finding.</b> Pneumonia has six positive held-out studies. Its metrics are "
 "descriptive and unstable, its sensitivity interval spans "
 + "%.2f&ndash;%.2f" % tuple(PF["Pneumonia"]["sens_ci"]) + ", and the all-finding macro "
 "average is correspondingly dominated by that term.",
 "<b>Partially trained model.</b> Eight of twenty epochs completed with the stopping criterion "
 "unsatisfied. The run is under-trained and its numbers are an early-run result.",
 "<b>Single seed.</b> No seed replication, no hyperparameter search and no variance estimate "
 "across runs are reported.",
 "<b>Label noise of unknown magnitude.</b> Targets are report-derived; no radiologist-annotated "
 "subset was used to estimate the noise rate, and the direction of the resulting bias is "
 "argued rather than measured.",
 "<b>Subgroup performance not assessed.</b> No stratified analysis by sex, age band, view "
 "position or reported race/ethnicity is reported. Because the model consumes sex and age "
 "directly, subgroup performance cannot be assumed uniform [16]&ndash;[19].",
 "<b>Calibration not assessed.</b> No reliability diagram, expected calibration error or "
 "recalibration is reported, and the weighted objective biases the probabilities by "
 "construction [15].",
 "<b>Shortcut controls not run.</b> The metadata-only control, the view-position permutation "
 "audit and the adversarial-invariance variant described in Section IV-F were specified and "
 "not executed, so the metadata channel remains a plausible shortcut carrier rather than a "
 "measured one.",
 "<b>Design risks unquantified.</b> Horizontal flipping is applied to a laterally organized "
 "finding, checkpoint selection minimizes a weighted loss, and the training-partition "
 "prevalences that determine the weights are not retained, so none of these choices can be "
 "audited from the release.",
 "<b>Evaluation-record gaps.</b> Per-study predictions, ROC coordinates, training and "
 "validation loss series, patient counts per partition, training prevalences and the subset "
 "selection rule are all absent from the release. Section IV-G documents the one consequence "
 "that affects a reported number, and {tab:T5} records the rest.",
 "<b>No reader study and no clinical validation.</b> No radiologist comparison, no "
 "time-to-decision measurement and no assessment of whether model output changes human "
 "performance are available [4]. The system is a research prototype and must not be used for "
 "medical decision-making.",
]),

("h1", "VI. CONCLUSION"),
("p",
 "This paper reported MediVision AI, a four-finding multimodal DenseNet121 baseline for chest "
 "radiograph classification, and an audit of the evaluation record that accompanies it. On a "
 "patient-disjoint " + str(N) + "-study held-out partition the framework reached a macro AUC "
 "of " + f(MAC["auc"]) + " over all four findings and " + f(MACR["auc"]) + " over the three "
 "findings with at least 30 positive studies, with the strongest discrimination for Pleural "
 "effusion (" + f(AUC["Pleural_Effusion"]) + ") and Cardiomegaly ("
 + f(AUC["Cardiomegaly"]) + ") and the weakest, on six positive studies, for Pneumonia ("
 + f(AUC["Pneumonia"]) + "). At a fixed threshold of 0.50 the model operated at macro "
 "sensitivity " + f(MAC["sens"]) + " and macro specificity " + f(MAC["spec"]) + " over all "
 "findings, and at " + f(MACR["sens"]) + " and " + f(MACR["spec"]) + " over the three "
 "substantial findings. Exact intervals are reported for every sensitivity and specificity, so "
 "the precision of each estimate is visible rather than implied."),
("p",
 "Four conclusions follow from the audit rather than from the score. First, the stored metric "
 "record is arithmetically closed and therefore usable: counts, rates and the macro average "
 "agree with one another exactly. Second, one archived ROC panel was not consistent with those "
 "counts, and the test that exposed it&mdash;an AUC that must lie inside the range attainable "
 "at its own operating point&mdash;is cheap enough that it should be part of any evaluation "
 "report. Third, the class-weighted objective cannot improve ranking metrics; it relocates the "
 "operating point instead, and the paper now states that instead of crediting the weighting "
 "with discrimination. Fourth, the claims that the current artifacts cannot support&mdash;a "
 "fusion benefit, a bootstrap interval, a calibrated probability, a subgroup difference&mdash;"
 "are all absent from this paper, and the artifact changes that would make each one computable "
 "are enumerated in {tab:T5}."),
("p",
 "The immediate work programme follows from that table and is short: persist per-study "
 "predictions and ROC coordinates at evaluation time; register image-only and metadata-only "
 "control checkpoints trained on the identical partition; complete the epoch budget with "
 "multiple seeds and select checkpoints by macro validation AUC; choose per-finding thresholds "
 "on the validation partition and report precision-recall curves; run the metadata permutation "
 "audit; and validate on a second institution's corpus. Until at least the first three are "
 "done, the framework is best described as a documented baseline for methodological study "
 "rather than as evidence about chest radiograph interpretation."),
]

EXTRA_BODY += [
("h1", "ACKNOWLEDGEMENT"),
("p",
 "The author thanks the maintainers of the public chest radiograph corpora used in this line "
 "of work for making de-identified research data available."),
("h1", "DECLARATIONS"),
("p",
 "<i>Ethics.</i> This study is a retrospective analysis of a public, de-identified secondary "
 "dataset (NIH ChestX-ray14, released under its own data-use agreement). It involved no "
 "prospective recruitment, no intervention and no access to identifiable patient information, "
 "so no new ethics approval or informed consent was required for the analysis reported here. "
 "Any clinical deployment would require ethics approval, regulatory review and prospective "
 "evaluation, none of which has been sought."),
("p",
 "<i>Data and code availability.</i> The implementation is released as a Python/PyTorch "
 "modelling package together with the archived evaluation record and the figures of this "
 "paper. The image corpus is not redistributed; it is available from its original providers "
 "under their own agreements. Model checkpoints and the corpus are excluded from version "
 "control, which is the specific reason an independent re-execution of the evaluation is not "
 "possible from the release alone (Section IV-H). A short reproduction script regenerates "
 "every table and figure in this paper from the released evaluation record, and every number "
 "in the tables is emitted by it rather than typed by hand."),
("p",
 "<i>Clinical disclaimer.</i> MediVision AI is a research prototype. Its outputs are model "
 "probabilities and not diagnoses, and Grad-CAM maps are attention diagnostics and not "
 "localizations of disease. The system must not be used for medical decision-making."),
]

EXTRA_BODY += [
("h1", "APPENDIX: CLAIM-TO-IMPLEMENTATION VERIFICATION"),
("p",
 "Each quantitative claim in Sections III and IV was checked directly against the "
 "implementation or the stored record; {tab:T6} records the outcome. Two entries removed "
 "content rather than confirming it. The evaluation stage retains no per-study prediction "
 "(V8), which is why the bootstrap intervals and the ablation cannot be computed; and no "
 "control model was trained (V9) and one archived ROC panel does not match the counts (V11), "
 "which is why the paper makes no fusion claim and plots no archived curve. Every other entry "
 "confirms that the methods text now describes the code."),
("table", "T6"),
]

TABLES2 = {
"T6": dict(
 caption="Claim-to-implementation verification. Each row was checked directly against the "
         "source; rows are ordered by the section they support.",
 header=["Item", "Claim in the manuscript", "Implementation or record as verified",
         "Section"],
 rows=[
   ["V1", "Positive weighting is pos_weight = N<sub>neg</sub>/N<sub>pos</sub> per finding",
    "Verified: per-finding counts are accumulated over the training loader and the ratio is "
    "passed to BCEWithLogitsLoss with denominators floored at 1 (Eq. 3)",
    "III-E"],
   ["V2", "Augmentation is affine and horizontal flip on training inputs only",
    "Verified: RandomAffine(degrees 5, translate 0.02, scale 0.97&ndash;1.03) and "
    "RandomHorizontalFlip(p 0.5); evaluation chain is resize and tensor conversion only",
    "III-C"],
   ["V3", "Normalization uses ImageNet mean and SD in both chains",
    "Verified: mean (0.485, 0.456, 0.406), SD (0.229, 0.224, 0.225)",
    "III-C"],
   ["V4", "Splitting is patient-level, 70/15/15, seed 42",
    "Verified by construction: the split is taken on unique patient identifiers; realized "
    "partition 3,447 / 722 / " + str(N) + " images",
    "III-B"],
   ["V5", "Evaluation uses one fixed threshold with no test-time tuning",
    "Verified: 0.50 is a constant in the metric function and no threshold search touches the "
    "test partition",
    "III-G"],
   ["V6", "Twenty epochs were requested; eight completed",
    "Verified: the configuration sets 20 epochs and patience 5; the run record reports 8 "
    "completed epochs with the stopping criterion unsatisfied",
    "III-F"],
   ["V7", "Checkpoints carry the per-epoch loss history and support resume",
    "Verified in code (model, optimizer, scheduler, epoch index, validation loss, history); no "
    "checkpoint is part of the release, so no history can be shown",
    "III-H"],
   ["V8", "Evaluation retains enough to support bootstrap intervals and an ablation",
    "Contradicted by the record: the evaluation entry point writes aggregate metrics and count "
    "matrices only, discarding per-study probabilities and patient identifiers",
    "IV-H"],
   ["V9", "Metadata fusion contributes to performance",
    "Unevidenced: no image-only or metadata-only checkpoint is registered, so no comparison "
    "exists in either direction",
    "IV-F"],
   ["V10", "Every reported metric is recomputable from the released artifacts",
    "Verified: all twenty stored quantities reproduce from the stored count matrices to "
    "machine precision, and every interval in {tab:T3B} is recomputed from those counts by the "
    "routines of Section III-G",
    "IV-G"],
   ["V11", "The archived ROC panel for Cardiomegaly describes the reported run",
    "Contradicted: the archived curve reaches TPR 0.96 at FPR "
    + f(PF["Cardiomegaly"]["rates"]["fpr"]) + " where the counts place the operating point at "
    "TPR " + f(PF["Cardiomegaly"]["rates"]["tpr"]) + "; an AUC of 0.957 lies outside the "
    "attainable range " + "%.3f&ndash;%.3f" % tuple(PF["Cardiomegaly"]["auc_bracket"]) + " of Eq. (7)",
    "IV-G"],
 ],
 note="Items V8, V9 and V11 removed or qualified content rather than confirming it. Items V1 "
      "to V7 confirm that the methods text is an accurate description of the code. {tab:T5} "
      "records the artifact changes that would let V8 and V9 be answered.",
),
}
