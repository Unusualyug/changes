# -*- coding: utf-8 -*-
"""Single source of truth for the manuscript text.

Inline markup supported by both renderers:
  <i>..</i>  <b>..</b>  <sub>..</sub>  <sup>..</sup>
Figures are referenced by key; paths live in FIGURES.
Tables are referenced as {tab:KEY}; figures as {fig:KEY}.

All derived numbers in this file are read from stats.json, which is produced by
stats.py from the archived evaluation record. Nothing here is typed by hand.
"""
import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(os.path.join(_HERE, "stats.json")))
PF = S["per_finding"]
REL = S["reliable_findings"]
REL_NAMES = {"Normal": "Normal", "Pneumonia": "Pneumonia",
             "Cardiomegaly": "Cardiomegaly", "Pleural_Effusion": "Pleural effusion"}


def f(x, nd=3):
    return ("%." + str(nd) + "f") % x


def ci(pair, nd=3):
    return "%.*f&ndash;%.*f" % (nd, pair[0], nd, pair[1])


# Convenience accessors so the prose cannot drift from the record.
AUC = {k: PF[k]["auc"] for k in PF}
AUCCI = {k: PF[k]["auc_ci_hanley"] for k in PF}
SENS = {k: PF[k]["rates"]["sens"] for k in PF}
SENSCI = {k: PF[k]["sens_ci"] for k in PF}
SPEC = {k: PF[k]["rates"]["spec"] for k in PF}
SPECCI = {k: PF[k]["spec_ci"] for k in PF}
PREC = {k: PF[k]["rates"]["prec"] for k in PF}
ACC = {k: PF[k]["rates"]["acc"] for k in PF}
CNT = {k: PF[k]["counts"] for k in PF}
MAC = S["macro_all"]
MACR = S["macro_reliable"]
MIC = S["micro"]
N = S["sample_count"]

TITLE = ("MediVision AI: A Multimodal DenseNet121 Baseline for Multi-Label Chest "
         "Radiograph Classification, with an Audit of What Its Evaluation Record "
         "Can and Cannot Support")

AUTHORS = "Y. Lakhani"
AFFIL = ("Department of Computer Engineering, GMIU<br/>"
         "Gujarat, India<br/>yglakhani@gmiu.edu.in")

ABSTRACT = (
 "Deep-learning prototypes for chest radiograph interpretation are abundant, but the "
 "evidence they ship with is often thinner than their reported scores. This paper "
 "reports MediVision AI, a compact research baseline that couples a DenseNet121 image "
 "encoder to a small metadata encoder and classifies four findings on a patient-disjoint "
 "split of a 4,999-image subset of NIH ChestX-ray14. On " + str(N) + " held-out studies, "
 "the recorded macro area under the ROC curve (AUC) is " + f(MAC["auc"]) + ". Restricting "
 "the macro average to the three findings with at least 30 positive studies gives "
 + f(MACR["auc"]) + ": Normal " + f(AUC["Normal"]) + " (95% interval " + ci(AUCCI["Normal"])
 + "), Cardiomegaly " + f(AUC["Cardiomegaly"]) + " (" + ci(AUCCI["Cardiomegaly"])
 + ") and Pleural effusion " + f(AUC["Pleural_Effusion"]) + " ("
 + ci(AUCCI["Pleural_Effusion"]) + "). Pneumonia has six positive studies and is reported "
 "descriptively only. Exact intervals for sensitivity and specificity are given throughout, "
 "and the small-event finding illustrates why they matter: its sensitivity is "
 + f(SENS["Pneumonia"]) + " with a 95% interval of " + ci(SENSCI["Pneumonia"], 2) + ". We "
 "then audit the evaluation record itself. Twenty stored metrics reproduce from the stored "
 "confusion counts to machine precision, but one archived ROC panel is inconsistent with "
 "those counts and is withdrawn rather than re-plotted. No image-only or metadata-only "
 "control was trained, so no fusion benefit is claimed; no threshold was selected on "
 "validation data; and per-study predictions were not retained, so patient-level bootstrap "
 "intervals remain unavailable. The contribution is a transparent baseline whose reported "
 "quantities are individually traceable to stored artifacts, together with an explicit "
 "account of the several things such a baseline cannot establish."
)

KEYWORDS = ("Chest radiography, class imbalance, DenseNet121, exact confidence intervals, "
            "label noise, multimodal fusion, reproducibility, shortcut learning.")

# ----------------------------------------------------------------------------- body
BODY = [
("h1", "I. INTRODUCTION"),
("p",
 "Chest radiography is the highest-volume diagnostic imaging examination worldwide, and the "
 "gap between examination volume and the availability of trained thoracic radiologists is "
 "widest in resource-constrained settings. Convolutional networks now reach "
 "radiologist-adjacent performance on selected chest radiograph tasks, which has produced a "
 "steady stream of prototype systems that convert a single frontal radiograph into "
 "finding-level probabilities. The empirical foundation of this literature is a small number "
 "of large public corpora annotated by mining radiology reports, of which NIH ChestX-ray14 "
 "and, more recently, MIMIC-CXR and CheXpert are the most frequently used [1]&ndash;[4]."),
("p",
 "The scientific value of such a prototype depends less on its headline area under the curve "
 "(AUC) than on whether its numbers can be traced to a defined model, a defined split and a "
 "defined evaluation script. Three failure modes recur. First, report-derived labels are "
 "noisy: the absence of a finding in a report is not evidence of its absence in the image, "
 "and multi-label targets built by string matching inherit this ambiguity [14]. Second, "
 "evaluation is frequently compromised either by patient-level leakage across splits or by "
 "silent changes of protocol between the training run and the reported table. Third, models "
 "readily exploit acquisition shortcuts&mdash;laterality markers, positioning devices, "
 "post-processing fingerprints and, in chest radiography, the anteroposterior versus "
 "posteroanterior projection&mdash;so that a measured association with disease may be an "
 "association with acquisition context [12], [13]."),
("p",
 "This paper reports MediVision AI, a four-finding chest radiograph baseline, and an audit of "
 "the evaluation record that accompanies it. We deliberately report the audit alongside the "
 "results rather than in a separate paper, because the two together determine what the "
 "numbers mean. The contributions are:"),
("bullets", [
 "<b>A fully specified, re-executable pipeline.</b> Data contract, patient-level splitting "
 "logic, transformation chain, normalisation constants, fusion architecture, objective and "
 "optimiser state are documented at the level of individual code paths (Section III), and "
 "every configuration value in the paper was read from the implementation rather than from "
 "earlier prose.",
 "<b>Held-out results with named denominators and exact intervals.</b> All metrics are "
 "reported on " + str(N) + " patient-disjoint studies at a single threshold of 0.50, with "
 "per-finding counts that reproduce the reported sensitivities and specificities exactly. "
 "Clopper-Pearson intervals are reported for every sensitivity and specificity and "
 "Hanley-McNeil intervals for every AUC (Sections IV-C, IV-D), which the earlier version of "
 "this work wrongly described as impossible; the Pneumonia interval, spanning "
 + ci(SENSCI["Pneumonia"], 2) + ", makes the small-event problem visible rather than "
 "rhetorical.",
 "<b>A restated macro average.</b> Because one modeled finding has six positive studies, we "
 "report the macro average over all four findings (" + f(MAC["auc"]) + ") together with a "
 "macro average restricted to the three findings that carry at least 30 positive studies ("
 + f(MACR["auc"]) + "), and we treat the second as the interpretable summary.",
 "<b>An audit of the evaluation record.</b> The stored metrics are arithmetically closed, "
 "but one archived ROC panel cannot describe the predictions summarized by the counts, and it "
 "is withdrawn from the paper rather than redrawn. Section IV-G states the test that any "
 "future figure must pass.",
]),
("p",
 "The scope statement matters as much as the results. MediVision AI is a research prototype. "
 "Its outputs are model probabilities, not diagnoses; its Grad-CAM maps are attention "
 "diagnostics, not localizations of disease; and the framework has had no reader study, no "
 "external validation and no calibration analysis. The multimodal design is described as a "
 "design, not as a demonstrated benefit: no image-only control was trained, so the paper "
 "makes no claim that metadata improves performance."),

("h1", "II. RELATED WORK"),
("h2", "A. Public Corpora and Report-Derived Labels"),
("p",
 "ChestX-ray14 introduced 112,120 frontal radiographs from 30,805 patients with fourteen "
 "finding labels extracted from reports by a rule-based labeller [1]; the subset used here is "
 "drawn from that corpus. MIMIC-CXR provides 377,110 images from 227,835 studies with paired "
 "free-text reports [2], and CheXpert contributes 224,316 radiographs with an explicit "
 "uncertainty category and a radiologist-annotated validation and test set [3]. The choice "
 "between corpora is essentially a choice of label-noise model: report-mined labels overstate "
 "prevalence, understate rare findings, and introduce systematic differences between the "
 "annotation process and the clinical question being studied; the concrete failure modes of "
 "the ChestX-ray14 labeller have been analysed in detail [10]. CheXNeXt showed that a "
 "carefully validated model can reach radiologist-level performance on selected findings [4], "
 "but that result rests on a purpose-built radiologist-annotated test set, which is precisely "
 "the resource most prototypes lack."),
("h2", "B. Architectures for Chest Radiograph Classification"),
("p",
 "DenseNet121 has become a common backbone for chest radiograph classification because dense "
 "connectivity reuses features aggressively in the data regime typical of medical imaging "
 "[5]; residual networks remain the standard alternative [6], and ImageNet pre-training is "
 "the default initialization for both [7]. At the scale studied here the classifier head, the "
 "input resolution and the fusion strategy plausibly dominate the reported performance more "
 "than the choice between densely and residually connected backbones, although this study "
 "does not test that claim: it uses one backbone and one resolution. Transfer learning from "
 "natural-image pre-training is the dominant recipe across medical imaging modalities, and "
 "the small-data regime in which it is used has been documented for retinal imaging as well "
 "as for thoracic imaging [22]."),
("h2", "C. Label Noise and Weak Supervision"),
("p",
 "Karimi et al. survey noise-robust training for medical image analysis and distinguish noise "
 "in feature space from noise in label space, observing that symmetric noise can be partly "
 "absorbed by regularization whereas asymmetric, class-dependent noise&mdash;the regime "
 "created by report mining&mdash;biases decision boundaries systematically [14]. For chest "
 "radiography the dominant asymmetry is that positive mentions are comparatively reliable "
 "while negative evidence is inferred from silence. Framing the task as multi-label sigmoid "
 "classification, as done here, avoids forcing a single mutually exclusive class but does not "
 "remove the underlying ambiguity."),
("h2", "D. Shortcut Learning and Spurious Correlation"),
("p",
 "Geirhos et al. define shortcut learning as the tendency of deep networks to adopt decision "
 "rules that perform well on a benchmark while violating the intended solution [12]. In chest "
 "radiography the canonical example is Zech et al., who showed that a pneumonia classifier "
 "transferred across institutions lost most of its apparent performance, and attributed the "
 "drop to hospital-specific markers and acquisition differences rather than to disease "
 "morphology [13]. Two consequences follow. First, a metadata channel that encodes view "
 "position, image dimensions and pixel spacing is a plausible shortcut carrier. Second, "
 "internal validation on a single-institution corpus cannot distinguish a learned disease "
 "signature from a learned acquisition signature, which is why external validation is listed "
 "as a hard limitation in Section V."),
("h2", "E. Calibration and Subgroup Fairness"),
("p",
 "Discrimination and calibration are distinct properties, and a model can rank cases well "
 "while producing probabilities that are systematically over- or under-confident; Van Calster "
 "et al. describe calibration as the weak point of clinical prediction models and recommend "
 "explicit calibration curves rather than AUC-only reporting [15]. Equity is the second axis: "
 "Seyyed-Kalantari et al. report underdiagnosis bias of chest radiograph classifiers in "
 "under-served populations [16], Larrazabal et al. show that gender imbalance in training "
 "data produces biased classifiers [17], Obermeyer et al. document how a proxy target can "
 "encode a protected attribute even when that attribute is never a feature [18], and Gichoya "
 "et al. demonstrate that patient race is recoverable from medical images alone [19]. A "
 "framework that ingests patient age and sex, as this one does, cannot claim subgroup "
 "neutrality by construction, and no subgroup analysis is reported here because the "
 "evaluation record does not retain per-patient predictions."),
("h2", "F. Multimodal Fusion of Imaging and Clinical Data"),
("p",
 "Baltrusaitis et al. provide the standard taxonomy of multimodal learning, distinguishing "
 "early, late and jointly learned fusion [20]. Huang et al. review fusion of medical imaging "
 "with electronic health records and emphasize that the incremental value of clinical "
 "variables is frequently confounded with acquisition metadata that co-varies with the "
 "clinical variable [21]. MediVision AI implements a late-fusion design in which a "
 "32-dimensional metadata embedding is concatenated with the pooled image descriptor. This is "
 "the cheapest possible fusion and, as Section IV-F argues, the design most exposed to "
 "shortcut acquisition of the metadata channel. Whether it helps at all is untested here."),
("h2", "G. Explainability and Its Limits"),
("p",
 "Grad-CAM produces coarse localization maps from the gradient of a target score with respect "
 "to a convolutional feature map [8], building on class activation mapping [9]. Such maps are "
 "widely presented as evidence of clinical plausibility, which overstates what a saliency map "
 "can establish: Rudin argues that post-hoc explanations of black-box models are unreliable "
 "substitutes for interpretable models in high-stakes decisions [11], and saliency maps are "
 "in general not unique, not stable under small perturbations and not formally faithful to "
 "the decision function. This framework therefore exposes Grad-CAM as a qualitative "
 "inspection aid for developers and not as a validation instrument. No saliency map is shown "
 "in this paper, because no radiograph and no checkpoint are part of the release; see "
 "Section V."),

("h1", "III. MATERIALS AND METHODS"),
("p",
 "The pipeline of {fig:pipeline} is summarized below. It covers the framework. The subsections below cover data assembly and "
 "partitioning (A&ndash;C), the multimodal encoder and its objective (D&ndash;E), and "
 "optimization and evaluation (F&ndash;H)."),
("fig", "pipeline"),
("h2", "A. Data Source and Label Construction"),
("p",
 "The study uses a 4,999-image working subset of the NIH ChestX-ray14 corpus [1], retained in "
 "the original NIH comma-separated metadata format with the columns <i>Image Index</i>, "
 "<i>Finding Labels</i>, <i>Patient ID</i>, <i>Patient Age</i>, <i>Patient Sex</i>, "
 "<i>View Position</i>, image dimensions and pixel spacing. Four findings are modeled: "
 "<i>Normal</i>, <i>Pneumonia</i>, <i>Cardiomegaly</i> and <i>Pleural effusion</i>. Binary "
 "targets are derived from the pipe-delimited <i>Finding Labels</i> field by a deterministic "
 "alias map, in which the literal token <i>No Finding</i> maps to Normal and the tokens "
 "<i>Effusion</i>, <i>Pleural Effusion</i> and <i>Pleural_Effusion</i> map to Pleural "
 "effusion. Because the task is multi-label, a study may be positive for more than one modeled "
 "finding, and the Normal indicator is treated as an ordinary target rather than as the "
 "complement of disease. Patient identifiers, study identifiers and follow-up indices are "
 "retained for traceability and excluded from all model inputs."),
("p",
 "Two properties of this construction bound what the Normal label means. It is not an "
 "independent radiological judgment: a study is Normal when the derived label vector is "
 "positive for <i>No Finding</i>, which is compatible with the report mentioning findings "
 "outside the four modeled here. And the modeled set is a four-of-fourteen projection of the "
 "corpus, chosen for tractability rather than by a principled selection rule; the resulting "
 "prevalences are reported in {tab:T1} and are specific to this subset. The released artifacts "
 "do not record how the 4,999-image subset was drawn (whether by random sampling, by "
 "stratification, or by taking a published Kaggle split), so the subset cannot be shown to be "
 "representative of ChestX-ray14, and the paper makes no such claim."),
("table", "T1"),
("h2", "B. Patient-Level Partitioning"),
("p",
 "Partitioning is performed on the unique patient identifier, not on the image. The patient "
 "list is shuffled with a fixed seed and split 70%, 15% and 15%; the image table is then "
 "filtered by membership. Splitting at the image level would let repeat examinations of the "
 "same patient appear on both sides of the split and would inflate held-out performance, an "
 "error that is common in chest radiograph benchmarks because the corpus contains several "
 "images per patient [1]. The realized partitions are 3,447 training, 722 validation and "
 + str(N) + " held-out images ({tab:T1}). The number of distinct patients is not stored in the "
 "released record, so the effective sample size of every interval in this paper is bounded "
 "below by the study count and above by the patient count; intervals are computed on studies "
 "and therefore ignore within-patient clustering, which makes them narrower than a "
 "patient-level interval would be. This is stated as a caveat wherever an interval is quoted."),
("h2", "C. Transformations and Augmentation"),
("p",
 "Training inputs are resized to 224&nbsp;&times;&nbsp;224, augmented with a random affine "
 "transform (rotation &plusmn;5&deg;, translation 2%, scale 0.97&ndash;1.03) and a random "
 "horizontal flip with probability 0.5; validation and test inputs receive resize and tensor "
 "conversion only. Both branches then apply channel-wise standardization with the ImageNet "
 "statistics &mu;&nbsp;=&nbsp;(0.485,&nbsp;0.456,&nbsp;0.406) and "
 "&sigma;&nbsp;=&nbsp;(0.229,&nbsp;0.224,&nbsp;0.225) [7]. Two properties deserve comment. "
 "First, the chain contains no intensity, contrast, gamma or histogram-equalization step, so "
 "the pipeline does not attempt to normalize the acquisition-dependent contrast differences "
 "that motivate external-validation failures [13]. Second, horizontal flipping is not "
 "label-preserving for every thoracic finding: it exchanges left and right, and Cardiomegaly "
 "in particular is a laterality-sensitive judgment because the cardiac silhouette is "
 "positioned on one side. Flipping was applied to all findings in training, and its effect on "
 "this finding is not measured here; it is recorded as a design risk in Section IV-F rather "
 "than as a verified harm."),
("h2", "D. Network Architecture"),
("p",
 "The image branch is DenseNet121 pre-trained on ImageNet, truncated at the global average "
 "pooling layer, giving a 1,024-dimensional descriptor. The metadata branch encodes an "
 "11-dimensional vector comprising age, original image width and height, x and y pixel "
 "spacing, one-hot encoding of patient sex (two levels plus an unknown bucket) and one-hot "
 "encoding of view position (posteroanterior, anteroposterior, unknown). Numeric metadata are "
 "scaled by fixed constants (age by 100, dimensions by 3,000, spacing by unity) so that each "
 "component lies approximately in [0,&nbsp;1]. A two-layer encoder maps the metadata vector "
 "to a 32-dimensional embedding; the two descriptors are concatenated and passed to a linear "
 "classifier with dropout. Writing <i>f</i><sub>&theta;</sub> for the image encoder, "
 "<i>g</i><sub>&phi;</sub> for the metadata encoder and <i>W</i>, <i>b</i> for the head, the "
 "model computes"),
("eq", (["z = W [ avgpool( f<sub>&theta;</sub>(x) ) ; g<sub>&phi;</sub>(m) ] + b,",
        "&nbsp;&nbsp;p<sub>c</sub> = &sigma;(z<sub>c</sub>)"], "1")),
("p",
 "where <i>x</i> is the image tensor, <i>m</i> the metadata vector and &sigma; the "
 "element-wise logistic function. When metadata are unavailable at inference time the branch "
 "receives a zero vector, which yields the encoder's learned bias response rather than an "
 "error; the service therefore degrades gracefully, but a missing-metadata prediction is not "
 "distributionally identical to a complete one."),
("h2", "E. Objective and Class Imbalance"),
("p",
 "The objective is a class-weighted binary cross-entropy over the four findings. For finding "
 "<i>c</i>, let N<sub>pos,c</sub> and N<sub>neg,c</sub> be the numbers of positive and "
 "negative training images and let <i>w</i><sub>c</sub> be the corresponding positive-class "
 "weight. The training loss is"),
("eq", (["L = &minus;(1/N) &Sigma;<sub>i</sub> &Sigma;<sub>c</sub> [ "
        "w<sub>c</sub> y<sub>ic</sub> ln p<sub>ic</sub>",
        "&nbsp;&nbsp;&nbsp;&nbsp;+ (1 &minus; y<sub>ic</sub>) ln(1 &minus; p<sub>ic</sub>) ]"], "2")),
("eq", (["w<sub>c</sub> = N<sub>neg,c</sub> / N<sub>pos,c</sub>"], "3")),
("p",
 "with p<sub>ic</sub> = &sigma;(z<sub>ic</sub>) and y<sub>ic</sub> &isin; {0,&nbsp;1}. The "
 "weighting is computed from the training partition only, and denominators are floored at one "
 "to avoid division by zero. Three consequences follow from Equation (3) directly."),
("bullets", [
 "<b>Positive weighting does not change ranking metrics.</b> Because "
 "w<sub>c</sub>&nbsp;&gt;&nbsp;1 is a strictly increasing rescaling of the positive term, it "
 "moves the iso-contour at a fixed threshold but not the ordering of scores within a finding. "
 "ROC-AUC is therefore invariant to the weighting, and any improvement in AUC attributed to "
 "w<sub>c</sub> could only be an artifact of training dynamics&mdash;different gradient "
 "magnitudes, hence a different parameter trajectory&mdash;not of the metric.",
 "<b>The weighting does move the operating point, and not necessarily in a useful direction.</b> "
 "The weight is largest where a finding is rarest, so the fixed 0.50 threshold lands at very "
 "different positions on different ROC curves. The largest weight belongs to the rarest "
 "modeled finding, which is why the operating point of the rarest finding is the least interpretable in the results; "
 "the training-partition positive counts that determine the individual weights are not "
 "retained in the released record, so the ordering of the weights can be inferred from the "
 "test prevalences only approximately and is not reported as a measured quantity.",
 "<b>The weighted loss is not comparable across findings.</b> Validation loss is a weighted "
 "quantity and must not be compared across findings or against unweighted literature values. "
 "It is used only for checkpoint selection within a single run.",
]),
("h2", "F. Optimization and Training Configuration"),
("p",
 "Training uses AdamW [23] with decoupled weight decay, a base learning rate of "
 "1&nbsp;&times;&nbsp;10<super>&minus;4</super>, weight decay 1&nbsp;&times;&nbsp;"
 "10<super>&minus;4</super>, mini-batches of 16 and a ReduceLROnPlateau schedule (factor 0.5, "
 "patience 2). Early stopping is configured with patience five epochs, and the checkpoint rule "
 "keeps the parameter set with the lowest weighted validation loss. Twenty epochs were "
 "requested and eight were completed; the stop is recorded as a completed run of eight "
 "epochs, not as a convergence decision, because the stopping criterion was never satisfied "
 "and no terminal event is logged. The model is therefore best read as partially trained: "
 "eight passes of a 3,447-image partition with one frozen-backbone epoch is a small budget, "
 "and the held-out AUCs reported here should be treated as an early-run result rather than a "
 "converged one. A single seed (42) controls patient splitting, weight initialization and the "
 "augmentation stream, and no replication across seeds is reported. {tab:T2} summarizes the "
 "configuration as read from the code."),
("table", "T2"),
("p",
 "One design decision in {tab:T2} deserves explicit criticism. Checkpoint selection minimizes "
 "the weighted validation loss of Equation (2). Because that loss sums four weighted "
 "per-finding terms, the finding with the largest weight dominates the selection criterion, "
 "and the validation partition has few positives for the rarest findings. A macro-averaged "
 "validation AUC would be a better selection criterion for a ranking problem, and its absence "
 "is a design weakness of the reported run rather than a property of the data."),
("h2", "G. Evaluation Metrics and Intervals"),
("p",
 "For each finding, with TP, TN, FP and FN denoting the entries of the 2&nbsp;&times;&nbsp;2 "
 "count matrix at threshold 0.50,"),
("eq", (["Sens = TP/(TP+FN),&nbsp;&nbsp; Spec = TN/(TN+FP),",
        "Prec = TP/(TP+FP),&nbsp;&nbsp; Acc = (TP+TN)/N"], "4")),
("eq", (["F1 = 2&middot;Prec&middot;Sens/(Prec+Sens)"], "5")),
("p",
 "and ROC-AUC is computed by the rank-based estimator. Macro aggregates are unweighted means "
 "over findings; micro aggregates pool the four 2&nbsp;&times;&nbsp;2 matrices into one count "
 "matrix, so a study contributes four label decisions. Macro and micro values therefore answer "
 "different questions&mdash;equal weight per finding versus equal weight per label "
 "decision&mdash;and both are reported because the corpus is severely imbalanced across "
 "findings (Section IV-A)."),
("p",
 "Two kinds of interval are reported, and neither requires per-study scores. For a "
 "sensitivity <i>k</i>/<i>n</i> the exact Clopper-Pearson interval is obtained by inverting the "
 "binomial test, using the beta quantiles "
 "B<sub>&alpha;/2</sub>(<i>k</i>,&nbsp;<i>n</i>&minus;<i>k</i>+1) and "
 "B<sub>1&minus;&alpha;/2</sub>(<i>k</i>+1,&nbsp;<i>n</i>&minus;<i>k</i>); Wilson score "
 "intervals are reported alongside in the supplementary record and differ from the exact "
 "intervals by less than 0.01 for all cells except Pneumonia. For an AUC with "
 "n<sub>pos</sub> positives and n<sub>neg</sub> negatives, the Hanley-McNeil variance "
 "approximation is"),
("eq", (["SE<sup>2</sup>(A) = [ A(1&minus;A) + (n<sub>pos</sub>&minus;1)(Q<sub>1</sub>&minus;A<sup>2</sup>)",
        "&nbsp;&nbsp;+ (n<sub>neg</sub>&minus;1)(Q<sub>2</sub>&minus;A<sup>2</sup>) ] / (n<sub>pos</sub>n<sub>neg</sub>),"], "6")),
("p",
 "with Q<sub>1</sub> = A/(2&minus;A) and Q<sub>2</sub> = 2A<sup>2</sup>/(1+A). Both "
 "constructions assume independent observations, so they ignore within-patient clustering and "
 "are slightly optimistic for that reason; the assumption is stated rather than corrected, "
 "because correcting it requires the patient identifiers that the record does not retain. "
 "Neither construction supports a comparison between two models, which would require paired "
 "resampling. Every interval quoted in Section IV is computed by the routine described here, "
 "and no interval is quoted anywhere in this paper that is not."),
("p",
 "A third quantity is reported for the AUCs and is not an interval in the statistical sense. "
 "The count matrix of each finding pins its ROC curve to a single point (FPR, TPR). Any "
 "non-decreasing curve from (0,&nbsp;0) to (1,&nbsp;1) through that point has an area bounded "
 "below by the piecewise-linear path through it and above by the path that rises to TPR = 1 "
 "before the point and stays there:"),
("eq", (["A<sub>min</sub> = &frac12;f&middot;t + (1&minus;f)t,&nbsp;&nbsp;"
        "A<sub>max</sub> = f&middot;t + (1&minus;f),"], "7")),
("p",
 "where <i>f</i> and <i>t</i> are the verified false- and true-positive rates. Both bounds are "
 "attainable, so Equation (7) gives the exact range of AUCs compatible with the counts, and a "
 "recorded AUC outside that range is not merely unlikely but impossible. This is the test "
 "applied in Section IV-G; because the bounds depend on a single operating point they are "
 "wide, and they are not a substitute for an interval."),
("h2", "H. Implementation"),
("p",
 "The reference implementation is written in Python with PyTorch [24] and torchvision for the "
 "backbone and transformation chain, scikit-learn for the rank statistics and count matrices, "
 "and matplotlib for figure generation. Training checkpoints carry the model state, optimizer "
 "and scheduler state, epoch index, validation loss and the running per-epoch history, which "
 "allows an interrupted run to resume from the last completed epoch. Evaluation is a separate "
 "entry point that reloads a saved checkpoint, reconstructs the deterministic test partition "
 "from the same seed and writes a structured JSON record. The separation is deliberate: the "
 "evaluation script never fits, tunes or selects anything, so the reported numbers cannot be "
 "contaminated by test-time decisions."),

("h1", "IV. RESULTS"),
("h2", "A. Corpus and Partition Composition"),
("p",
 "{tab:T1} gives the realized partition sizes and the held-out prevalence of each modeled "
 "finding. Two features dominate the interpretation of every later table. First, the findings "
 "are not merely imbalanced but separated by nearly two orders of magnitude: 451 of "
 + str(N) + " held-out studies are labeled Normal whereas only 6 are labeled Pneumonia. "
 "Second, the positive labels are not mutually exclusive, so the " + str(N) + " studies "
 "contribute 643 positive label decisions across the four findings. Any unweighted macro "
 "average therefore contains a term estimated from six events, and its sampling variability is "
 "dominated by that term."),
("h2", "B. Training Behaviour"),
("p",
 "The released record states the number of completed epochs, eight, together with the "
 "evaluated metrics. It states nothing about the shape of the loss trajectory: the training "
 "loop accumulates a per-epoch history in memory and writes it only into a checkpoint, and no "
 "checkpoint is part of the release. No training-curve figure can therefore be drawn from the "
 "released artifacts, and this paper contains none. What is claimed is limited to two facts "
 "recorded in the run: eight of the twenty budgeted epochs completed, and the early-stopping "
 "criterion was never satisfied during those eight epochs. The practical implication is stated "
 "in Section III-F: the model is partially trained, and its held-out numbers should be read as "
 "an early-run result."),
("h2", "C. Held-Out Discrimination"),
("p",
 "{tab:T3} reports per-finding performance on the " + str(N) + " held-out studies at the fixed "
 "threshold of 0.50, and {fig:roc} shows the operating points and the AUC intervals. "
 "Discrimination is moderate and heterogeneous. Pleural effusion is the best-ranked finding "
 "(AUC " + f(AUC["Pleural_Effusion"]) + ", 95% interval " + ci(AUCCI["Pleural_Effusion"])
 + ") and Normal the weakest of the three substantial findings ("
 + f(AUC["Normal"]) + ", " + ci(AUCCI["Normal"]) + "). Cardiomegaly sits between them at "
 + f(AUC["Cardiomegaly"]) + " (" + ci(AUCCI["Cardiomegaly"]) + "), and the two Cardiomegaly "
 "and effusion estimates are close enough that their intervals nearly touch, so the paper does "
 "not rank them. Pneumonia's recorded AUC of " + f(AUC["Pneumonia"]) + " rests on six positive "
 "studies; its interval (" + ci(AUCCI["Pneumonia"]) + ") spans almost the entire admissible "
 "range, and it is reported for completeness only."),
("table", "T3"),
("table", "T3B"),
("fig", "roc"),
("p",
 "The macro AUC over all four findings, " + f(MAC["auc"]) + ", is the arithmetic mean of the "
 "four recorded values and inherits the six-event Pneumonia term. Restricting the mean to the "
 "three findings with at least 30 positive studies gives " + f(MACR["auc"]) + " with a macro "
 "sensitivity of " + f(MACR["sens"]) + " and a macro specificity of " + f(MACR["spec"])
 + " at the fixed threshold; the corresponding all-finding values are " + f(MAC["sens"])
 + " and " + f(MAC["spec"]) + ". We report both and treat the three-finding average as the "
 "interpretable summary, because an unweighted mean that gives a sixth of its weight to a "
 "finding with six positives is not a summary of anything stable. Neither value is comparable "
 "to AUCs reported on radiologist-annotated test sets [4] or on the full fourteen-finding "
 "benchmark [1]: the cohort, the label construction and the finding set all differ."),
("h2", "D. Operating-Point Behaviour and Intervals"),
("p",
 "{tab:T4} decomposes the same results into confusion counts, and {fig:confusion} shows "
 "the four matrices. The macro sensitivity of " + f(MAC["sens"]) + " against a macro "
 "specificity of " + f(MAC["spec"]) + " describes a model that is conservative on "
 "Cardiomegaly (sensitivity " + f(SENS["Cardiomegaly"]) + " at specificity "
 + f(SPEC["Cardiomegaly"]) + ") and permissive on Pleural effusion (sensitivity "
 + f(SENS["Pleural_Effusion"]) + " at specificity " + f(SPEC["Pleural_Effusion"]) + "). The "
 "operating points are the best-corroborated quantities in the study, because they follow "
 "arithmetically from count matrices that each account for all " + str(N) + " studies."),
("table", "T4"),
("fig", "confusion"),
("p",
 "With intervals attached, three of these operating points sharpen and one collapses. "
 "Pleural effusion sensitivity " + f(SENS["Pleural_Effusion"]) + " ("
 + ci(SENSCI["Pleural_Effusion"]) + ") and specificity " + f(SPEC["Pleural_Effusion"]) + " ("
 + ci(SPECCI["Pleural_Effusion"]) + ") are estimated precisely enough to support the "
 "statement that the model runs at a high-sensitivity, low-specificity point for this "
 "finding. Cardiomegaly sensitivity " + f(SENS["Cardiomegaly"]) + " ("
 + ci(SENSCI["Cardiomegaly"]) + ") does not support a claim of conservative behaviour in "
 "either direction with confidence, although its specificity "
 + f(SPEC["Cardiomegaly"]) + " (" + ci(SPECCI["Cardiomegaly"]) + ") is well estimated. "
 "Pneumonia is uninterpretable at this denominator: sensitivity " + f(SENS["Pneumonia"])
 + " with a 95% interval of " + ci(SENSCI["Pneumonia"], 2) + ", and specificity "
 + f(SPEC["Pneumonia"]) + " (" + ci(SPECCI["Pneumonia"]) + ") estimated from a class in which "
 "the model predicts positive for roughly half of all negatives. A single decision moves "
 "Pneumonia sensitivity by 0.167, and precision of " + f(PREC["Pneumonia"]) + " reflects four "
 "correct positives among " + str(CNT["Pneumonia"]["tp"] + CNT["Pneumonia"]["fp"])
 + " positive predictions."),
("p",
 "The Normal finding produces " + str(CNT["Normal"]["fn"]) + " false negatives: studies "
 "labeled Normal that the model flags as abnormal. Because the four targets are independent "
 "sigmoids, this is the signature of a model that over-predicts disease when the label set is "
 "dominated by negative evidence, and it is the largest single contributor to the gap between "
 "per-finding accuracy (" + f(ACC["Normal"]) + ") and the specificity of the disease findings. "
 "Pleural effusion generates " + str(CNT["Pleural_Effusion"]["fp"]) + " false positives, the "
 "price of a high positive weight. Precision is low for every finding except Normal, which "
 "follows directly from low prevalence and is the reason precision and recall must be read "
 "together at a stated prevalence."),
("h2", "E. What the Counts Imply About the Curves"),
("p",
 "Because the pipeline stores only aggregate metrics, the interior of each ROC curve is not "
 "recoverable from the release: no per-study score vector, and no false- or true-positive-rate "
 "array, survives in it. Aggregated metrics do not determine the shape of a ROC curve, and "
 "this paper therefore does not plot one. What the counts do determine is (i) the single "
 "operating point of each finding, (ii) the exact range of AUCs compatible with that point, "
 "given by Equation (7), and (iii) intervals from the binomial and Hanley-McNeil "
 "constructions of Section III-G. The first two are shown in {fig:roc}, and all three are "
 "tabulated in {tab:T3B} and {tab:T4}."),
("p",
 "The attainable range in {fig:roc}(b) is reported because it converts a qualitative doubt "
 "into a checkable inequality. For Normal the recorded AUC of " + f(AUC["Normal"])
 + " lies inside the range [%.3f, %.3f]" % tuple(PF["Normal"]["auc_bracket"]) + "; for "
 "Cardiomegaly " + f(AUC["Cardiomegaly"]) + " lies inside "
 + "[%.3f, %.3f]" % tuple(PF["Cardiomegaly"]["auc_bracket"]) + "; and for Pleural effusion "
 + f(AUC["Pleural_Effusion"]) + " lies inside "
 + "[%.3f, %.3f]" % tuple(PF["Pleural_Effusion"]["auc_bracket"]) + ". A recorded value that fell "
 "outside its own range would be arithmetically impossible rather than merely imprecise. This "
 "test, not a visual comparison of curves, is what the audit in Section IV-G rests on."),
("h2", "F. Design Risks and What This Study Cannot Say"),
("p",
 "The most consequential design risk in this framework is that the metadata encoder receives "
 "view position as a one-hot input. Posteroanterior and anteroposterior projections are not "
 "exchangeable: anteroposterior views are acquired predominantly in patients who are "
 "bed-bound, portable or acutely unwell, whereas posteroanterior views are acquired in "
 "ambulatory patients standing at a dedicated unit. The projection is therefore correlated "
 "with illness severity, examination setting and the reporting pathway that produces the "
 "label. A model that learns &lsquo;anteroposterior implies disease&rsquo; can reduce loss "
 "without learning anything about lung morphology, and the correlation is strong enough that "
 "the behaviour would not be visible in an aggregate AUC. Image dimensions and pixel spacing "
 "carry a weaker but similar signal, since they fingerprint the acquisition device."),
("p",
 "This risk has two implications the present study cannot resolve. First, any performance gain "
 "attributed to metadata fusion must be read as an acquisition-context effect until the "
 "opposite is demonstrated, and the demonstration requires an ablation comparing image-only, "
 "metadata-only and fused models on the same partition with paired intervals. No such "
 "ablation exists here: a single fused model was trained, and no control checkpoints were "
 "registered. The framework therefore supports no claim about fusion benefit in either "
 "direction, and the paper makes none. Second, a metadata-only control is the cheapest "
 "available diagnostic&mdash;if a model that never sees the image attains non-trivial AUC, the "
 "fused model's gain is contaminated by construction&mdash;and running it is listed as "
 "outstanding work in Section V. The permutation audit described below is likewise specified "
 "and not run: score each held-out study twice, once with its observed metadata and once with "
 "the view-position field permuted across studies, and report the change in AUC per finding."),
("p",
 "Three further design elements are recorded here as risks rather than results. Horizontal "
 "flipping is applied to Cardiomegaly despite the finding's laterality dependence, and the "
 "effect is unmeasured. The fixed threshold of 0.50 is not a decision rule: the validation "
 "partition exists, was used for checkpoint selection, and was not used to choose per-finding "
 "thresholds or to produce precision-recall curves, which are the appropriate summary at these "
 "prevalences. And the Normal label is not an independent radiological category, as Section "
 "III-A explains, so Normal performance partly measures the model's ability to recognize "
 "findings it does not model."),
("h2", "G. Provenance of the Archived ROC Figure"),
("p",
 "The release contains a ROC figure and a confusion figure alongside the JSON metric record. "
 "The metric record is arithmetically closed: for each finding, the stored count matrix "
 "reproduces the stored sensitivity, specificity, precision and F1, every matrix sums to "
 + str(N) + ", and the stored macro AUC equals the mean of the four per-finding AUCs to six "
 "decimal places. The confusion figure agrees with those matrices in the rank order of its "
 "cell shadings for all four findings. The ROC figure is the exception. It stores no numeric "
 "coordinates&mdash;the pipeline writes only a rendered image&mdash;so it can be measured but "
 "not recomputed, and for Cardiomegaly what it yields is incompatible with the rest of the "
 "record: the archived curve reaches a true-positive rate of about 0.96 at the false-positive "
 "rate of " + f(PF["Cardiomegaly"]["rates"]["fpr"]) + " where the counts place the operating "
 "point at " + f(PF["Cardiomegaly"]["rates"]["tpr"]) + "."),
("p",
 "Equation (7) settles the question. A monotone ROC curve through "
 "(" + f(PF["Cardiomegaly"]["rates"]["fpr"]) + ", "
 + f(PF["Cardiomegaly"]["rates"]["tpr"]) + ") has an area between "
 + "%.3f and %.3f" % tuple(PF["Cardiomegaly"]["auc_bracket"]) + ". The recorded AUC of "
 + f(AUC["Cardiomegaly"]) + " lies in that range; the value obtained by integrating the "
 "archived curve for this finding, 0.957, does not. The archived panel is therefore withdrawn "
 "from this paper rather than redrawn. The reported Cardiomegaly AUC remains "
 + f(AUC["Cardiomegaly"]) + ", the value in the internally consistent record."),
("p",
 "Two statements bound what this resolution establishes. First, it does not re-derive the "
 "reported value: no curve was stored for Cardiomegaly, and re-establishing one requires "
 "re-running evaluation, which the release does not permit because the checkpoint and the "
 "image corpus are excluded from version control. The value is reported as recorded and "
 "arithmetically consistent, not as independently recomputed. Second, the fault is confined to "
 "the archived panel: the counts, the metric record and the confusion figure agree with each "
 "other, so the discrepancy is most consistent with a stale or partially regenerated panel "
 "rather than with a corrupted evaluation. The test that any replacement figure must pass is "
 "stated here: its operating point must reproduce the counts to within 0.01, and its integral "
 "must equal the recorded AUC to within 0.01."),
("h2", "H. Statistical Analysis: What Is and Is Not Reported"),
("p",
 "The protocol called for 95% confidence intervals from patient-level bootstrap resampling of "
 "the held-out studies over 2,000 replicates, and for a paired bootstrap over 2,000 replicates "
 "to quantify the difference between the fused model and an image-only control. Neither is "
 "available, for a checkable reason: the evaluation entry point writes per-finding aggregate "
 "metrics and a count matrix but discards the per-study predicted probabilities, so the "
 "resampling unit&mdash;the study, with its patient identifier and label vector&mdash;cannot "
 "be reconstructed from the release. The first of these two gaps is partly closed here by "
 "distribution-free constructions that need only counts (Section III-G), in place of the resampling approach of Efron and Tibshirani [25]: exact intervals are "
 "now reported for every sensitivity and specificity, and Hanley-McNeil intervals for every "
 "AUC. What remains unavailable is anything that requires pairing: the absolute interval on a "
 "macro average, subgroup strata, calibration, and any model-to-model comparison. {tab:T5} "
 "lists each estimand, its status, and the artifact change that would unblock it."),
("p",
 "One consequence deserves emphasis. The difference between the reported macro AUC and any "
 "literature value is uninterpretable without an interval on the difference, and the ablation "
 "is not merely unquantified but unrun: no image-only checkpoint is registered, so no "
 "statement about the value of metadata fusion can be made from this study in either "
 "direction."),
("table", "T5"),
]

# ----------------------------------------------------------------------------- tables
TABLES = {
"T1": dict(
 caption="Corpus and held-out composition. Split sizes are images; the nominal 70/15/15 "
         "allocation is applied to patients, and the realized image fractions differ because "
         "studies per patient vary.",
 header=["Partition / finding", "Images", "Share", "Positives", "Prevalence"],
 rows=[
   ["Training", "3,447", "68.95%", "&mdash;", "&mdash;"],
   ["Validation", "722", "14.44%", "&mdash;", "&mdash;"],
   ["Test", str(N), "16.60%", "643<super>a</super>", "&mdash;"],
   ["&nbsp;&nbsp;Normal", str(N), "&mdash;", "451", "0.543"],
   ["&nbsp;&nbsp;Pneumonia", str(N), "&mdash;", "6", "0.007"],
   ["&nbsp;&nbsp;Cardiomegaly", str(N), "&mdash;", "73", "0.088"],
   ["&nbsp;&nbsp;Pleural effusion", str(N), "&mdash;", "113", "0.136"],
   ["Total", "4,999", "100%", "&mdash;", "&mdash;"],
 ],
 note="<super>a</super> Positive label decisions summed across the four findings; the "
      "targets are not mutually exclusive, so this exceeds the number of studies. "
      "Per-finding positive counts for the training and validation partitions are not "
      "retained in the released metric record and are therefore not reported; the training "
      "prevalences that determine the weights of Equation (3) cannot be quoted for the same "
      "reason.",
),
"T2": dict(
 caption="Training configuration as read from the implementation.",
 header=["Parameter", "Value", "Source of record"],
 rows=[
   ["Optimizer", "AdamW (&beta;<sub>1</sub> 0.9, &beta;<sub>2</sub> 0.999)", "code"],
   ["Learning rate", "1 &times; 10<super>&minus;4</super>", "code / config"],
   ["Weight decay", "1 &times; 10<super>&minus;4</super>", "code / config"],
   ["Batch size", "16", "code / config"],
   ["Epochs requested / completed", "20 / 8", "config / run record"],
   ["Early-stopping patience", "5 epochs (weighted validation loss)", "code / config"],
   ["LR schedule", "ReduceLROnPlateau (factor 0.5, patience 2)", "code"],
   ["Random seed", "42 (split, init, augmentation)", "code / config"],
   ["Patient-level split", "70 / 15 / 15", "code"],
   ["Input resolution", "224 &times; 224 &times; 3", "code / metadata"],
   ["Normalization", "ImageNet mean and SD", "code"],
   ["Augmentation", "Affine &plusmn;5&deg;, translate 2%, scale 0.97&ndash;1.03; "
                    "h-flip p = 0.5", "code"],
   ["Dropout", "0.20 (metadata encoder, head)", "code"],
   ["Loss", "BCEWithLogits, pos_weight = N<sub>neg</sub>/N<sub>pos</sub>", "code"],
   ["Threshold", "0.50 (fixed, not tuned on test)", "code"],
 ],
 note="The completed-epoch count is eight of a requested twenty. The run stopped short of its "
      "budget with the stopping criterion unsatisfied and no terminal event logged, so the "
      "model is described as partially trained rather than converged.",
),
"T3": dict(
 caption="Held-out performance at a fixed threshold of 0.50 (n = " + str(N) + " studies). "
         "AUC is threshold-free; the other columns are computed at the fixed point. The 95% "
         "intervals for every AUC, sensitivity and specificity appear in {tab:T3B}.",
 header=["Finding", "AUC", "Sens.", "Spec.", "Prec.", "F1"],
 rows=[
   ["Normal", f(AUC["Normal"]), f(SENS["Normal"]), f(SPEC["Normal"]),
    f(PREC["Normal"]), f(PF["Normal"]["f1"])],
   ["Pneumonia<super>b</super>", f(AUC["Pneumonia"]), f(SENS["Pneumonia"]),
    f(SPEC["Pneumonia"]), f(PREC["Pneumonia"]), f(PF["Pneumonia"]["f1"])],
   ["Cardiomegaly<super>c</super>", f(AUC["Cardiomegaly"]), f(SENS["Cardiomegaly"]),
    f(SPEC["Cardiomegaly"]), f(PREC["Cardiomegaly"]), f(PF["Cardiomegaly"]["f1"])],
   ["Pleural effusion", f(AUC["Pleural_Effusion"]), f(SENS["Pleural_Effusion"]),
    f(SPEC["Pleural_Effusion"]), f(PREC["Pleural_Effusion"]), f(PF["Pleural_Effusion"]["f1"])],
   ["<b>Macro (4)</b>", "<b>" + f(MAC["auc"]) + "</b>",
    "<b>" + f(MAC["sens"]) + "</b>", "<b>" + f(MAC["spec"]) + "</b>",
    "<b>" + f(MAC["prec"]) + "</b>", "&mdash;"],
   ["<b>Macro (3)<super>d</super></b>", "<b>" + f(MACR["auc"]) + "</b>",
    "<b>" + f(MACR["sens"]) + "</b>", "<b>" + f(MACR["spec"]) + "</b>",
    "<b>" + f(MACR["prec"]) + "</b>", "&mdash;"],
   ["Micro", "&mdash;", f(MIC["rates"]["sens"]), f(MIC["rates"]["spec"]),
    f(MIC["rates"]["prec"]), f(MIC["f1"])],
 ],
 note="<super>b</super> Six positive studies. Every quantity in this row is descriptive; the "
      "sensitivity interval spans " + ci(SENSCI["Pneumonia"], 2) + " and a single decision "
      "moves it by 0.167. <super>c</super> The AUC is the value in the archived metric record; "
      "its ROC panel was not archived in a form consistent with the counts and is withdrawn "
      "(Section IV-G). <super>d</super> Unweighted mean over Normal, Cardiomegaly and Pleural "
      "effusion, the findings with at least 30 positive studies. Micro aggregates pool the "
      "four count matrices. No interval is reported for a macro average: the variance of an "
      "average of dependent per-finding estimates cannot be computed from aggregate counts, "
      "and no pairing information survives in the record.",
),
"T3B": dict(
 caption="95% intervals for the held-out estimates of {tab:T3}. Sensitivity and specificity "
         "intervals are exact (Clopper-Pearson); AUC intervals use the Hanley-McNeil "
         "variance of Eq. (6). All four constructions assume independent studies and "
         "therefore ignore within-patient clustering.",
 header=["Finding", "AUC 95% CI", "Sens. 95% CI", "Spec. 95% CI"],
 rows=[
   ["Normal", ci(AUCCI["Normal"]), ci(SENSCI["Normal"]), ci(SPECCI["Normal"])],
   ["Pneumonia<super>b</super>", ci(AUCCI["Pneumonia"]), ci(SENSCI["Pneumonia"], 2),
    ci(SPECCI["Pneumonia"])],
   ["Cardiomegaly", ci(AUCCI["Cardiomegaly"]), ci(SENSCI["Cardiomegaly"]),
    ci(SPECCI["Cardiomegaly"])],
   ["Pleural effusion", ci(AUCCI["Pleural_Effusion"]), ci(SENSCI["Pleural_Effusion"]),
    ci(SPECCI["Pleural_Effusion"])],
 ],
 note="The Pneumonia row is the reason intervals are reported at all: its sensitivity "
      "interval spans " + ci(SENSCI["Pneumonia"], 2) + " on six positive studies, so no "
      "statement about its operating point can be supported. Intervals for the macro averages "
      "are not reported; see the note to {tab:T3}.",
),
"T4": dict(
 caption="Verified confusion counts at threshold 0.50, with the operating point they imply "
         "and the range of AUCs attainable by any monotone ROC curve through that point "
         "(Eq. 7). Every matrix accounts for all " + str(N) + " held-out studies; the "
         "operating point is (FPR, TPR) = (FP/(FP+TN), TP/(TP+FN)).",
 header=["Finding", "TN", "FP", "FN", "TP", "AUC range"],
 rows=[
   [k.replace("_", " "), str(CNT[k]["tn"]), str(CNT[k]["fp"]), str(CNT[k]["fn"]),
    str(CNT[k]["tp"]), "%.3f&ndash;%.3f" % tuple(PF[k]["auc_bracket"])]
   for k in ["Normal", "Pneumonia", "Cardiomegaly", "Pleural_Effusion"]
 ] + [
   ["<b>Pooled</b>", "<b>" + str(MIC["counts"]["tn"]) + "</b>",
    "<b>" + str(MIC["counts"]["fp"]) + "</b>", "<b>" + str(MIC["counts"]["fn"]) + "</b>",
    "<b>" + str(MIC["counts"]["tp"]) + "</b>", "&mdash;"],
 ],
 note="Counts and every rate derived from them were recomputed from the released record and "
      "agree exactly. The attainable range is the exact interval of ROC areas compatible with "
      "a single operating point; it is wide by construction and is a consistency check, not a "
      "confidence interval. Normal's operating point is (0.208, 0.530), Pneumonia's (0.482, "
      "0.667), Cardiomegaly's (0.137, 0.479) and Pleural effusion's (0.354, 0.876). The "
      "recorded AUC of every finding lies inside its own range.",
),
"T5": dict(
 caption="Statistical estimands called for by the protocol, their status, the requirement "
         "that blocks each one, and what this paper reports instead.",
 header=["Estimand", "Status", "Blocker", "Reported instead"],
 widths=[1.05, 0.55, 1.30, 0.95],
 rows=[
   ["95% CI for sensitivity / specificity at 0.50", "Reported",
    "None: exact binomial inversion needs only the counts",
    "Exact binomial, {tab:T3B}"],
   ["95% CI for per-finding AUC", "Reported",
    "None: Hanley-McNeil variance needs only the AUC and class sizes",
    "Hanley-McNeil, {tab:T3B}"],
   ["95% CI for macro AUC (patient-level bootstrap)",
    "Not computed", "Per-study probabilities and patient IDs are discarded by the evaluation "
    "script; the variance of a mean of dependent AUCs has no closed form",
    "Macro reported, no interval"],
   ["Paired bootstrap: fused vs image-only", "Not run",
    "Requires an image-only checkpoint on the identical partition plus paired per-study "
    "predictions", "No fusion claim (IV-F)"],
   ["Subgroup metrics (sex, age band, view)", "Not computed",
    "Requires retained per-study metadata alongside predictions", "Not reported"],
   ["Calibration (reliability curve, ECE)", "Not computed",
    "Requires retained probabilities; ECE needs bin-wise counts", "Not reported"],
   ["Threshold selection on validation data", "Not performed",
    "No validation predictions were retained or used", "Single fixed threshold, 0.50"],
 ],
 note="Intervals that need only counts are now reported; every quantity that needs pairing, "
      "resampling or per-study scores remains unavailable and is not estimated.",
),
}
