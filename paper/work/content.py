# -*- coding: utf-8 -*-
"""Single source of truth for the manuscript text.

Inline markup supported by both renderers:
  <i>..</i>  <b>..</b>  <sub>..</sub>  <sup>..</sup>
Figures are referenced by key; paths live in FIGURES.
"""

TITLE = ("MediVision AI: A Reproducible Multimodal DenseNet121 Framework for "
         "Multi-Label Chest Radiograph Classification with a Documented "
         "Implementation and Statistical-Reporting Audit")

AUTHORS = "Y. Lakhani"
AFFIL = ("Department of Computer Engineering, GMIU<br/>"
         "Gujarat, India<br/>yglakhani@gmiu.edu.in")

ABSTRACT = (
 "Automated interpretation of chest radiographs is one of the most widely studied "
 "applications of deep learning in medicine, yet a substantial share of published "
 "prototypes cannot be reproduced from the artifacts that accompany them. This paper "
 "reports MediVision AI, an end-to-end framework for multi-label chest radiograph "
 "classification that couples a DenseNet121 image encoder with a compact metadata "
 "encoder in a late-fusion head, trained with a class-weighted binary cross-entropy "
 "objective and evaluated on a patient-disjoint held-out partition. On a 830-study "
 "held-out test set drawn from a 4,999-image subset of the NIH ChestX-ray14 corpus, "
 "the model attained a macro area under the receiver operating characteristic curve "
 "(AUC) of 0.771, with per-finding AUCs of 0.724 (Normal), 0.709 (Pneumonia), 0.805 "
 "(Cardiomegaly) and 0.844 (Pleural effusion); macro sensitivity, specificity, "
 "precision and F1 at a 0.50 threshold were 0.638, 0.705, 0.323 and 0.349, "
 "respectively, and micro-averaged F1 was 0.407. Because the pipeline emits only "
 "aggregate metrics, 95% bootstrap confidence intervals and a paired bootstrap "
 "ablation are specified but not computed here, and the paper abstains from "
 "inferential claims that these intervals would require. In addition to the "
 "quantitative results, the paper contributes a claim-to-implementation verification "
 "matrix covering the loss weighting, augmentation set, normalisation statistics and "
 "patient-level splitting logic, an audit of what the current evaluation artifacts "
 "can and cannot support statistically, and a verified reference set in which every "
 "entry was resolved against a registry record. The framework, the evaluation "
 "protocol and the reported numbers are intended as a defensible baseline rather "
 "than as evidence of clinical readiness: no reader study, no external validation "
 "and no calibration analysis have been performed."
)

KEYWORDS = ("Bootstrap confidence intervals, chest radiography, class imbalance, "
            "DenseNet121, label noise, multimodal fusion, reproducibility, "
            "shortcut learning, subgroup fairness.")

# ----------------------------------------------------------------------------- body
# Each item: ("h1"/"h2"/"p"/"eq"/"fig"/"table"/"bullets"/"note", payload)
BODY = [
("h1", "I. INTRODUCTION"),
("p",
 "Chest radiography remains the highest-volume diagnostic imaging examination "
 "worldwide, and the gap between examination volume and the availability of trained "
 "thoracic radiologists is widest in resource-constrained settings. Convolutional "
 "neural networks have repeatedly been shown to reach radiologist-level or "
 "radiologist-adjacent performance on selected chest radiograph tasks, and this has "
 "produced a sustained stream of prototype systems that convert a single frontal "
 "radiograph into a set of finding-level probabilities. The empirical foundation of "
 "this literature is a small number of large public corpora annotated by mining "
 "radiology reports, of which NIH ChestX-ray14 and, more recently, MIMIC-CXR and "
 "CheXpert are the most frequently used [1]&ndash;[4]."),
("p",
 "The scientific value of a prototype, however, depends less on its headline area "
 "under the curve than on whether its numbers can be traced to a defined model, a "
 "defined split and a defined evaluation script. Three failure modes recur. First, "
 "report-derived labels are noisy: the absence of a finding in a radiology report is "
 "not evidence of its absence in the image, and multi-label targets built by string "
 "matching inherit this ambiguity [14]. Second, evaluation is frequently compromised "
 "either by patient-level leakage across splits or by silent changes of protocol "
 "between the training run and the reported table. Third, models readily exploit "
 "acquisition shortcuts, including laterality markers, positioning devices, "
 "post-processing fingerprints and, in chest radiography, the anteroposterior versus "
 "posteroanterior projection, so that a measured association with disease may in "
 "fact be an association with the acquisition context [12], [13]."),
("p",
 "This paper reports MediVision AI, a chest radiograph classification framework whose "
 "public value is deliberately weighted towards auditability. The contributions are "
 "as follows."),
("bullets", [
 "<b>A pipeline specification at implementation level.</b> The data contract, "
 "splitting logic, transformation chain, normalisation constants, fusion "
 "architecture, objective and optimiser state are documented to the level of "
 "individual code paths, and the manuscript text is reconciled against them rather "
 "than the reverse (Section III, {tab:T6}).",
 "<b>A held-out evaluation with named denominators.</b> All metrics are reported on a "
 "830-study test partition that is disjoint from training and validation at the "
 "patient level, at a single operating point of 0.50, with per-finding confusion "
 "counts that reproduce the reported sensitivities and specificities exactly "
 "(Tables III and IV).",
 "<b>An audit of statistical claims.</b> The paper states precisely which inferential "
 "quantities the current artifacts can support. Because the evaluation pipeline "
 "writes aggregate metrics only, patient-level bootstrap intervals and a paired "
 "bootstrap ablation are specified but not computed, and no confidence interval is "
 "reported ({tab:T5}, Section IV-F).",
 "<b>A corrected premise about class weighting.</b> The loss weighting implemented in "
 "the code is pos_weight = N<sub>neg</sub> / N<sub>pos</sub> per finding, and the "
 "manuscript states explicitly that this weighting does not alter the ranking "
 "metrics (ROC-AUC) that are reported, contrary to a common but incorrect "
 "assumption that reweighting improves ranking.",
 "<b>A verified reference set.</b> Every bibliographic entry was resolved against a "
 "registry record during revision; two widely mis-cited page ranges and one "
 "non-resolving conference DOI were corrected or replaced, and all recorded "
 "corrections are listed in Appendix A.",
]),
("p",
 "The scope statement matters as much as the results. MediVision AI is a research "
 "prototype. Its outputs are model probabilities, not diagnoses; its Grad-CAM maps "
 "are attention diagnostics, not localisations of disease; and the framework has not "
 "been subjected to a reader study, external validation or a calibration analysis. "
 "The paper is written so that a reader can verify every number it contains against "
 "the released artifacts, and so that the absence of an interval is visible rather "
 "than concealed."),

("h1", "II. RELATED WORK"),
("h2", "A. Public Corpora and Report-Derived Labels"),
("p",
 "ChestX-ray14 introduced 112,120 frontal radiographs from 30,805 patients with "
 "fourteen finding labels extracted from reports by a rule-based labeller [1]; the "
 "subset used here is drawn from that corpus. MIMIC-CXR provides 377,110 images from "
 "227,835 studies with paired free-text reports [2], and CheXpert contributes 224,316 "
 "radiographs with an explicit uncertainty category and a radiologist-annotated "
 "validation and test set [3]. The choice between these corpora is essentially a "
 "choice of label noise model: report-mined labels overstate disease prevalence, "
 "understate rare findings, and introduce systematic differences between the "
 "annotation process and the clinical question being studied; the concrete failure modes of the "
 "ChestX-ray14 labeller have been analysed in detail [10]. CheXNeXt demonstrated "
 "that a carefully validated model can reach radiologist-level performance on "
 "selected findings [4], but this result was obtained with a purpose-built "
 "radiologist-annotated test set, which is precisely the resource that most "
 "prototypes lack."),
("h2", "B. Architectures for Chest Radiograph Classification"),
("p",
 "DenseNet121 has become the de facto backbone for chest radiograph classification "
 "because dense connectivity reuses features aggressively in the data regime typical "
 "of medical imaging [5]; residual networks remain the standard alternative [6], and "
 "ImageNet pre-training is the default initialisation for both [7]. Equation-level "
 "details of the dense block are not reproduced here; the relevant engineering "
 "observation is that the classifier head, the input resolution and the fusion "
 "strategy dominate the reported performance far more than the choice between "
 "densely and residually connected backbones at this data scale. Aside from chest "
 "radiography, transfer learning from natural-image pre-training is the dominant recipe "
 "across medical imaging modalities, and the small-data regime in which it is used has "
 "been documented for retinal imaging as well as for thoracic imaging [22]."),
("h2", "C. Label Noise and Weak Supervision"),
("p",
 "Karimi et al. survey noise-robust training for medical image analysis and "
 "distinguish between noise in the feature space and noise in the label space, "
 "observing that symmetric noise can be partially absorbed by regularisation whereas "
 "asymmetric, class-dependent noise&mdash;the regime created by report mining&mdash;"
 "biases decision boundaries systematically [14]. For chest radiography the dominant "
 "asymmetry is that positive mentions are comparatively reliable while negative "
 "evidence is inferred from silence. Framing the task as multi-label sigmoid "
 "classification, as done here, avoids forcing a single mutually exclusive class but "
 "does not remove the underlying label ambiguity."),
("h2", "D. Shortcut Learning and Spurious Correlation"),
("p",
 "Geirhos et al. define shortcut learning as the tendency of deep networks to adopt "
 "decision rules that perform well on a benchmark while violating the intended "
 "solution [12]. In chest radiography the canonical example is Zech et al., who "
 "showed that a pneumonia classifier transferred across institutions lost most of its "
 "apparent performance, and attributed the drop to hospital-specific markers and "
 "acquisition differences rather than to disease morphology [13]. Two consequences "
 "follow for the present work. First, a metadata channel that encodes view position, "
 "image dimensions and pixel spacing is a plausible shortcut carrier; Second, "
 "internal validation on a single-institution corpus cannot distinguish a learned "
 "disease signature from a learned acquisition signature, which is why external "
 "validation is listed as a hard limitation in Section VI."),
("h2", "E. Calibration and Subgroup Fairness"),
("p",
 "Discrimination and calibration are distinct properties, and a model can rank cases "
 "well while producing probabilities that are systematically over- or "
 "under-confident; Van Calster et al. describe calibration as the weak point of "
 "clinical prediction models and recommend explicit calibration curves and "
 "recalibration rather than AUC-only reporting [15]. Equity is the second axis: "
 "Seyyed-Kalantari et al. report underdiagnosis bias of chest radiograph classifiers "
 "in under-served populations [16], Larrazabal et al. show that gender imbalance in "
 "training data produces biased classifiers [17], Obermeyer et al. document how a "
 "proxy target can encode a protected attribute even when that attribute is never "
 "used as a feature [18], and Gichoya et al. demonstrate that patient race is "
 "recoverable from medical images alone [19]. A framework that ingests patient age "
 "and sex, as this one does, cannot claim subgroup neutrality by construction, and "
 "no subgroup analysis is reported here because the evaluation artifacts do not "
 "retain per-patient predictions."),
("h2", "F. Multimodal Fusion of Imaging and Clinical Data"),
("p",
 "Baltrusaitis et al. provide the standard taxonomy of multimodal learning, "
 "distinguishing early, late and jointly learned fusion [20]. Huang et al. review "
 "fusion of medical imaging with electronic health records and emphasise that the "
 "incremental value of clinical variables is frequently confounded with acquisition "
 "metadata that co-varies with the clinical variable [21]. MediVision AI implements a "
 "late-fusion design in which a 32-dimensional metadata embedding is concatenated "
 "with the pooled image descriptor. This is the cheapest possible fusion and, as "
 "Section V-C argues, precisely the design most exposed to shortcut acquisition of "
 "the metadata channel."),
("h2", "G. Explainability and Its Limits"),
("p",
 "Grad-CAM produces coarse localisation maps from the gradient of a target score with "
 "respect to a convolutional feature map [8], building on class activation mapping "
 "[9]. Such maps are widely presented as evidence of clinical plausibility, which "
 "overstates what a saliency map can establish: Rudin argues that post-hoc "
 "explanations of black-box models are unreliable substitutes for interpretable "
 "models in high-stakes decisions [11], and saliency maps are in general not unique, "
 "not stable under small input perturbations and not faithful to the model's "
 "decision function in any formal sense. The present framework therefore exposes "
 "Grad-CAM as a qualitative inspection aid for developers and not as a validation "
 "instrument; Section VI records the absence of a sanity check of the kind used to "
 "test saliency reliability."),
("h2", "H. Evaluation Protocol Adopted in This Paper"),
("p",
 "The protocol below is stated before the results so that every later number can be "
 "checked against it."),
("bullets", [
 "<b>Partition.</b> Seventy, fifteen and fifteen percent of <i>patients</i>, drawn "
 "without replacement using a fixed seed; the unit of splitting is the patient "
 "identifier, and no patient contributes images to more than one partition.",
 "<b>Operating point.</b> A single global threshold of 0.50 applied to sigmoid "
 "outputs for every finding; no per-finding threshold tuning is performed, and "
 "therefore no threshold is selected on the test data.",
 "<b>Metrics.</b> Per-finding ROC-AUC, sensitivity, specificity, precision, F1 and "
 "accuracy, together with macro and micro aggregates across findings. AUC is "
 "threshold-free; the remaining metrics are reported at the single fixed point.",
 "<b>Reporting rule.</b> A metric is reported only if it can be recomputed from the "
 "committed artifacts. Where an inferential quantity (confidence interval, paired "
 "difference) cannot be computed from what was retained, the paper states this "
 "explicitly instead of quoting an estimate.",
]),

("h1", "III. MATERIALS AND METHODS"),
("p",
 "Fig. {fig:pipeline} summarises the framework end to end. The subsections below follow "
 "its three stages: data assembly and partitioning (A&ndash;C), the multimodal encoder and "
 "its objective (D&ndash;E), and optimisation and evaluation (F&ndash;H)."),
("fig", "pipeline"),
("h2", "A. Data Source and Label Construction"),
("p",
 "The study uses a 4,999-image working subset of the NIH ChestX-ray14 corpus [1], "
 "retained in the original NIH comma-separated metadata format with the columns "
 "<i>Image Index</i>, <i>Finding Labels</i>, <i>Patient ID</i>, <i>Patient Age</i>, "
 "<i>Patient Sex</i>, <i>View Position</i>, image dimensions and pixel spacing. Four "
 "findings are modelled: <i>Normal</i>, <i>Pneumonia</i>, <i>Cardiomegaly</i> and "
 "<i>Pleural effusion</i>. Binary targets are derived from the pipe-delimited "
 "<i>Finding Labels</i> field by a deterministic alias map, in which the literal "
 "token <i>No Finding</i> maps to Normal and the tokens <i>Effusion</i>, <i>Pleural "
 "Effusion</i> and <i>Pleural_Effusion</i> map to Pleural effusion. Because the task "
 "is multi-label, a single study may be positive for more than one modelled finding, "
 "and the Normal indicator is treated as an ordinary target rather than as the "
 "complement of disease. Patient identifiers, study identifiers and follow-up "
 "indices are retained for traceability and excluded from all model inputs."),
("h2", "B. Patient-Level Partitioning"),
("p",
 "Partitioning is performed on the unique patient identifier, not on the image. The "
 "patient list is shuffled with a fixed seed and split into 70%, 15% and 15% "
 "partitions; the image table is then filtered by membership. Splitting at the image "
 "level would allow repeat examinations of the same patient to appear on both sides "
 "of the split and would inflate held-out performance, an error that is common in "
 "chest radiograph benchmarks because the corpus contains several images per patient. "
 "The implementation asserts patient-disjointness by construction, and the realized "
 "partition sizes are 3,447 / 722 / 830 images, i.e. 68.95% / 14.44% / 16.60% of the "
 "corpus, the deviation from the nominal 70/15/15 arising because images rather than "
 "patients are counted after the split. No patient-level overlap exists between the "
 "three partitions; {tab:T6} records the corresponding verification. {tab:T1} reports "
 "the realized composition and the held-out prevalence of each modelled finding."),
("table", "T1"),
("h2", "C. Pre-processing, Augmentation and Normalisation"),
("p",
 "All images are converted to three-channel RGB, resized to 224&nbsp;&times;&nbsp;224 "
 "and scaled to [0,&nbsp;1]. Training inputs pass through random affine "
 "transformation (&plusmn;5&deg; rotation, &plusmn;2% translation, scale 0.97&ndash;"
 "1.03) and random horizontal flipping with probability 0.5; validation and test "
 "inputs receive resize and tensor conversion only. Both branches then apply "
 "channel-wise standardisation with the ImageNet statistics "
 "&mu;&nbsp;=&nbsp;(0.485,&nbsp;0.456,&nbsp;0.406) and "
 "&sigma;&nbsp;=&nbsp;(0.229,&nbsp;0.224,&nbsp;0.225) [7]. Two properties of this "
 "chain deserve comment. First, the transformation list contains no intensity, "
 "contrast, gamma or histogram-equalisation step, so the pipeline does not attempt to "
 "normalise the strong acquisition-dependent contrast differences that motivate "
 "external-validation failures [13]. Second, horizontal flipping is not label "
 "preserving in a strict sense: it exchanges left and right and would be "
 "inappropriate for tasks whose labels are lateralised, although the four findings "
 "modelled here are not."),
("h2", "D. Network Architecture"),
("p",
 "The image branch is DenseNet121 pre-trained on ImageNet, truncated at the global "
 "average pooling layer, giving a 1,024-dimensional descriptor. The metadata branch "
 "encodes an 11-dimensional vector comprising age, original image width and height, "
 "x and y pixel spacing, one-hot encoding of patient sex (two levels plus an unknown "
 "bucket) and one-hot encoding of view position (posteroanterior, anteroposterior, "
 "unknown). Numeric metadata are scaled by fixed constants (age by 100, dimensions by "
 "3,000, spacing by unity) so that each component lies approximately in [0,&nbsp;1]. "
 "A two-layer encoder maps the metadata vector to a 32-dimensional embedding, and the "
 "two descriptors are concatenated and passed to a linear classifier with dropout. "
 "Writing <i>f</i><sub>&theta;</sub> for the image encoder, <i>g</i><sub>&phi;</sub> "
 "for the metadata encoder and <i>W</i>, <i>b</i> for the head, the model computes"),
("eq", (["z = W [ avgpool( f<sub>&theta;</sub>(x) ) ; g<sub>&phi;</sub>(m) ] + b,"
         "&nbsp;&nbsp;p<sub>c</sub> = &sigma;(z<sub>c</sub>)"], "1")),
("p",
 "where <i>x</i> is the image tensor, <i>m</i> the metadata vector and &sigma; the "
 "element-wise logistic function. When metadata are unavailable at inference time the "
 "branch is fed a zero vector, which yields the encoder's learned bias response "
 "rather than an error; this behaviour is implemented deliberately so that the "
 "service degrades gracefully, but it also means that a missing-metadata prediction "
 "is not distributionally identical to a complete one."),
("h2", "E. Objective and Class Imbalance"),
("p",
 "The objective is a class-weighted binary cross-entropy over the four findings. For "
 "finding <i>c</i>, let N<sub>pos,c</sub> and N<sub>neg,c</sub> be the numbers of "
 "positive and negative training images, and let <i>w</i><sub>c</sub> be the "
 "corresponding positive-class weight. The training loss is"),
("eq", (["L = &minus;(1/N) &Sigma;<sub>i</sub> &Sigma;<sub>c</sub> [ "
         "w<sub>c</sub> y<sub>ic</sub> ln p<sub>ic</sub>",
         "&nbsp;&nbsp;&nbsp;&nbsp;+ (1 &minus; y<sub>ic</sub>) ln(1 &minus; p<sub>ic</sub>) ]"], "2")),
("eq", (["w<sub>c</sub> = N<sub>neg,c</sub> / N<sub>pos,c</sub>"], "3")),
("p",
 "with p<sub>ic</sub> = &sigma;(z<sub>ic</sub>) and y<sub>ic</sub> &isin; {0,&nbsp;1}. "
 "The weighting is computed from the training partition only, and the denominators are "
 "floored at one to avoid division by zero for findings that are absent from a "
 "partition. The implementation was audited against Equations (2) and (3) and matches "
 "them exactly ({tab:T6}); three practical consequences follow, and the correction of "
 "the manuscript's earlier framing of this point is recorded explicitly."),
("bullets", [
 "<b>Positive weighting does not change ranking metrics.</b> Because "
 "w<sub>c</sub>&nbsp;&gt;&nbsp;1 is a strictly increasing rescaling of the positive "
 "term, it changes the location of the iso-contour at a fixed threshold but not the "
 "ordering of scores within a finding. ROC-AUC is therefore invariant to the "
 "weighting, and any improvement in AUC attributed to <i>w</i><sub>c</sub> would be "
 "an artefact of the training dynamics (different gradient magnitudes, hence a "
 "different parameter trajectory), not of the metric itself. The manuscript must not "
 "claim that the weighting improves discrimination.",
 "<b>The weighting does move the operating point.</b> With w<sub>c</sub> = "
 "N<sub>neg,c</sub>/N<sub>pos,c</sub>, the model's posterior at p = 0.5 corresponds "
 "to a prior-corrected decision, so sensitivity at the fixed threshold rises and "
 "specificity falls for the heavily weighted findings. {tab:T3} shows exactly this "
 "pattern for Pleural effusion, where sensitivity (0.876) is far above specificity "
 "(0.646).",
 "<b>The reported loss is therefore not comparable across findings.</b> Validation "
 "loss is a weighted quantity and must not be compared across findings or against "
 "unweighted literature values; it is used only for checkpoint selection within a "
 "single run.",
]),
("h2", "F. Optimisation and Training Configuration"),
("p",
 "Training uses AdamW [23] with decoupled weight decay, a base learning rate of "
 "1&nbsp;&times;&nbsp;10<super>&minus;4</super>, weight decay 1&nbsp;&times;&nbsp;"
 "10<super>&minus;4</super>, mini-batches of 16 and a ReduceLROnPlateau schedule "
 "(factor 0.5, patience 2) driven by validation loss. Early stopping is configured "
 "with a patience of five epochs against validation loss, and the best-checkpoint rule "
 "saves the parameter set with the lowest validation loss. Twenty epochs were "
 "requested; the registered run completed eight epochs and the lowest validation loss "
 "occurred at the final epoch, so the early-stopping criterion was never triggered. "
 "A single seed (42) controls patient splitting, weight initialisation and the "
 "augmentation stream, and no replication across seeds is reported. {tab:T2} "
 "summarises the configuration as read from the code rather than from the "
 "manuscript, and is placed here, rather than in an appendix, because the two differ."),
("table", "T2"),
("h2", "G. Evaluation Metrics"),
("p",
 "For each finding, with TP, TN, FP and FN denoting the entries of the 2&nbsp;&times;"
 "&nbsp;2 count matrix at threshold 0.50,"),
("eq", (["Sens = TP/(TP+FN),&nbsp;&nbsp; Spec = TN/(TN+FP),",
         "Prec = TP/(TP+FP),&nbsp;&nbsp; Acc = (TP+TN)/N"], "4")),
("eq", (["F1 = 2&middot;Prec&middot;Sens/(Prec+Sens)"], "5")),
("p",
 "and ROC-AUC is computed by the rank-based estimator. Macro aggregates are unweighted "
 "means over the four findings; micro aggregates pool the four 2&nbsp;&times;&nbsp;2 "
 "matrices into a single count matrix, so a study contributes four label decisions. "
 "Macro and micro values consequently answer different questions&mdash;equal weight "
 "per finding versus equal weight per label decision&mdash;and both are reported "
 "because the corpus is severely imbalanced across findings (Section IV-A)."),
("h2", "H. Implementation"),
("p",
 "The reference implementation is written in Python with PyTorch [24] and torchvision "
 "for the backbone and transformation chain, scikit-learn for the rank statistics and "
 "count matrices, and matplotlib for figure generation. Training checkpoints carry the "
 "model state, optimiser and scheduler state, epoch index, validation loss and the "
 "per-epoch history, which allows an interrupted run to resume from the last completed "
 "epoch. Evaluation is a separate entry point that reloads the saved checkpoint, "
 "reconstructs the deterministic test partition from the same seed and writes a "
 "structured JSON record of the metrics. This separation is deliberate: the "
 "evaluation script never fits, tunes or selects anything, so the reported numbers "
 "cannot be contaminated by test-time decisions."),

("h1", "IV. RESULTS"),
("h2", "A. Corpus and Partition Composition"),
("p",
 "{tab:T1} gives the realized partition sizes and the held-out prevalence of each "
 "modelled finding. Two features dominate the interpretation of every later table. "
 "First, the findings are not merely imbalanced but separated by nearly two orders of "
 "magnitude: 451 of 830 held-out studies are labelled Normal whereas only 6 are "
 "labelled Pneumonia. Second, the positive labels are not mutually exclusive, so the "
 "830 studies contribute 643 positive label decisions across the four findings. Any "
 "macro average therefore contains a term estimated from six events, and its sampling "
 "variability is dominated by that term."),
("h2", "B. Training Behaviour"),
("p",
 "Validation loss decreased from 0.1595 at epoch 1 to 0.1485 at epoch 8, with a "
 "single non-monotone step at epoch 6 (0.1489) that was too small to trigger the "
 "plateau schedule. The best checkpoint coincides with the last completed epoch, so "
 "the model reported here is the least-regularised of the eight, and the absence of a "
 "later upturn means that over-fitting was not observed on the validation partition "
 "within the budget. This is a statement about the validation loss of the weighted "
 "objective, which is dominated by the Normal finding because of its prevalence, and "
 "not a statement that the other three decision boundaries were still improving; a "
 "per-finding validation curve is not retained by the pipeline and is listed as a "
 "reporting gap in Section VII."),
("fig", "loss"),
("h2", "C. Held-Out Discrimination"),
("p",
 "{tab:T3} reports per-finding performance on the 830 held-out studies at the fixed "
 "threshold of 0.50, and {fig:roc} shows the corresponding ROC curves. Discrimination "
 "is moderate and heterogeneous. Pleural effusion and Cardiomegaly are ranked most "
 "reliably (AUC 0.844 and 0.805), Normal is intermediate (0.724) and Pneumonia is "
 "lowest (0.709) on a denominator of six positive studies. The macro AUC of 0.771 "
 "should be read as a summary of a heterogeneous set of tasks rather than as a single "
 "performance level, and it is not directly comparable to macro AUCs reported on "
 "radiologist-annotated test sets [4] or on the full fourteen-finding benchmark [1]."),
("table", "T3"),
("fig", "roc"),
("h2", "D. Operating-Point Behaviour"),
("p",
 "{tab:T4} and {fig:confusion} decompose the same results into confusion counts. The macro "
 "sensitivity of 0.638 against a macro specificity of 0.705 describes a model that is "
 "conservative on Cardiomegaly (sensitivity 0.479 at specificity 0.863) and permissive "
 "on Pleural effusion (sensitivity 0.876 at specificity 0.646). The two behaviours are "
 "consistent with the weighting scheme of Equation (3): effusion has the largest "
 "positive weight in the training partition and Cardiomegaly among the smallest, so "
 "the fixed threshold of 0.50 sits at very different positions on their respective "
 "operating curves. Precision is low for every finding except Normal, which is a "
 "direct consequence of low prevalence and is the reason precision and recall must be "
 "read together at a stated prevalence."),
("table", "T4"),
("fig", "confusion"),
("p",
 "Three specific error modes are visible. First, the Normal finding produces 212 false "
 "negatives: studies labelled Normal that the model flags as abnormal. Because the "
 "four targets are independent sigmoids, this is the signature of a model that "
 "over-predicts disease when the label set is dominated by negative evidence, and it "
 "is the single largest contributor to the gap between per-finding accuracy (0.649) "
 "and the specificity of the disease findings. Second, Pleural effusion generates 254 "
 "false positives, the price of the high positive weight. Third, Pneumonia is "
 "uninterpretable: with six positives in 830 studies, a single decision changes "
 "sensitivity by 0.167, so neither the AUC of 0.709 nor the sensitivity of 0.667 can "
 "be treated as an estimate of anything stable. Reporting that value without this "
 "caveat would be misleading, and the paper therefore flags it as descriptive only."),
("h2", "E. Statistical Analysis: Plan, Status and Consequences"),
("p",
 "The protocol calls for 95% confidence intervals obtained by resampling the held-out "
 "studies at the patient level with 2,000 replicates, and for a paired bootstrap "
 "over 2,000 replicates to quantify the difference between the full multimodal model "
 "and an image-only ablation [25]. Neither quantity is available, for a precise and "
 "checkable reason: the evaluation entry point writes per-finding aggregate metrics "
 "and a count matrix but discards the per-study predicted probabilities, so the "
 "resampling unit (the study, together with its patient identifier and label vector) "
 "cannot be reconstructed from the released artifacts. {tab:T5} records the specified "
 "estimands, their status and the minimal artifact change that would make each one "
 "computable. The paper does not report an interval, a standard error, a p-value or a "
 "paired difference for any metric, and no text in this version claims that such "
 "quantities will be reported."),
("table", "T5"),
("p",
 "Two consequences of this gap are worth stating plainly. First, the difference "
 "between the reported macro AUC of 0.771 and any literature value is uninterpretable "
 "without an interval, because the intervals implied by 830 studies with a six-event "
 "finding are wide. Second, the ablation is not merely unquantified but unrun: no "
 "image-only checkpoint is registered alongside the multimodal one, so the claim that "
 "metadata fusion contributes to performance is unsupported by this study in either "
 "direction. Section V-C treats this as a substantive result rather than as a "
 "bookkeeping omission."),

("h1", "V. DISCUSSION"),
("h2", "A. What the Numbers Do and Do Not Establish"),
("p",
 "The results establish that a DenseNet121 plus metadata late-fusion model, trained "
 "for eight epochs under a class-weighted objective on a 3,447-image training "
 "partition, ranks held-out studies for Pleural effusion and Cardiomegaly "
 "substantially better than chance, and ranks them for Pneumonia at a level that "
 "cannot be distinguished from a coarse estimate. They do not establish clinical "
 "utility. Utility requires, at minimum, a discrimination level measured against a "
 "radiologist-annotated reference, a calibration curve, a decision-threshold analysis "
 "with explicit costs, and evidence of transportability to a second institution. None "
 "of these are present, and the corresponding limitations are enumerated in "
 "Section VI rather than absorbed into the discussion."),
("h2", "B. Label Quality as the Dominant Uncertainty"),
("p",
 "The error modes in {tab:T4} are more plausibly attributable to label construction "
 "than to model capacity. A study is labelled Normal when the report contains no "
 "positive finding, which conflates a genuinely normal examination with an "
 "under-reported one; a study is labelled Pneumonia only when the report uses that "
 "token, which is rare in a corpus in which pneumonia is typically described "
 "descriptively. The asymmetric noise regime described by Karimi et al. [14] "
 "therefore applies with full force: the positive class is comparatively clean, the "
 "negative class is contaminated, and the classifier is pushed towards "
 "over-prediction, which is exactly the pattern of 212 Normal false negatives and 254 "
 "effusion false positives. Under this reading, the largest available improvement is "
 "not architectural but annotational&mdash;an expert-annotated evaluation subset of "
 "even a few hundred studies would sharpen the estimates more than any change of "
 "backbone."),
("h2", "C. View Position as a Shortcut, and Why the Metadata Channel Is Suspect"),
("p",
 "The most consequential design risk in this framework is that the metadata encoder "
 "receives view position as a one-hot input. Posteroanterior and anteroposterior "
 "projections are not exchangeable: anteroposterior views are acquired predominantly "
 "in patients who are bed-bound, portable or acutely unwell, whereas posteroanterior "
 "views are acquired in ambulatory patients standing at a dedicated unit. The "
 "projection is therefore correlated with illness severity, with examination setting "
 "and with the technologist, radiologist and downstream reporting pathway that "
 "produce the label. A model that learns &lsquo;anteroposterior implies disease&rsquo; "
 "can achieve a real reduction in loss without learning anything about lung "
 "morphology, and the correlation is strong enough that the behaviour would not be "
 "visible in an aggregate AUC. Image dimensions and pixel spacing carry a weaker but "
 "similar signal, since they fingerprint the acquisition device."),
("p",
 "This risk has three concrete implications. First, any performance gain attributed to "
 "metadata fusion must be interpreted as an acquisition-context effect until the "
 "opposite is demonstrated, and the correct demonstration is an ablation that "
 "compares image-only, metadata-only and fused models on the same partition, with "
 "confidence intervals on the paired differences; none of these comparisons is "
 "available here. Second, a metadata-only control is the cheapest diagnostic "
 "available: if a model that never sees the image attains non-trivial AUC, the fused "
 "model's gain is contaminated by construction. Third, the deployment implication is "
 "that a model trained under this design may not transfer to a setting with a "
 "different projection mix even if the patient population is similar, which is a "
 "specific and testable prediction rather than a generic caution."),
("p",
 "Two mitigations are appropriate and neither is implemented in the present version. "
 "The first is a counterfactual audit: score every held-out study twice, once with "
 "its observed metadata and once with the view-position field permuted across "
 "studies, and report the change in AUC per finding. A large drop localises the "
 "dependence without requiring retraining. The second is architectural: remove view "
 "position from the metadata vector and retain only age and sex, or route the "
 "metadata through a gradient-reversal adversary that is trained to predict view "
 "position from the embedding, so that the representation is discouraged from "
 "carrying acquisition information. Both are cheap relative to the cost of a "
 "retraining campaign and should precede any claim about multimodal benefit."),
("h2", "D. Class Imbalance, Thresholding and the Meaning of 0.50"),
("p",
 "The fixed threshold of 0.50 is appropriate for an evaluation protocol, because it "
 "prevents the test set from being used to select an operating point, but it is not a "
 "clinical decision rule. With positive weighting the implicit prior differs across "
 "findings, so a single threshold places the four decision boundaries at "
 "inconsistent positions on their ROC curves, as {tab:T3} demonstrates. A deployment "
 "would require per-finding thresholds selected on validation data against explicit "
 "costs, and the validation partition exists for exactly that purpose but was not used "
 "for it here."),
("h2", "E. Reliability, Calibration and Subgroup Behaviour"),
("p",
 "No calibration analysis is reported. The weighted objective deliberately distorts "
 "the predicted probabilities relative to the empirical frequencies, so the outputs "
 "must not be interpreted as risk. For a screening aid this matters less than for a "
 "triage tool, but it matters for any downstream use that combines the probability "
 "with a prior. On subgroup behaviour, the framework ingests age and sex as features "
 "and reports no stratified metrics; given the documented underdiagnosis bias of chest "
 "radiograph classifiers in under-served populations [16] and the gender-imbalance "
 "effects reported by Larrazabal et al. [17], the absence of a subgroup table is a "
 "gap that the current artifacts cannot close, because the evaluation record does not "
 "retain per-study predictions and therefore cannot be re-aggregated by subgroup "
 "without re-running evaluation."),
("h2", "F. Explainability"),
("p",
 "Grad-CAM maps are produced by the service for qualitative inspection. They are "
 "computed from the gradient of a single logit with respect to the final "
 "convolutional feature map, upsampled to input resolution and overlaid on the "
 "radiograph [8]. The framework does not include a sanity check of the kind that tests "
 "whether the map depends on the model at all (for example, comparison against a "
 "randomly initialised network or against a cascading parameter randomisation), and "
 "the maps are therefore not offered as evidence that the model attends to "
 "anatomical structures. This is consistent with the position that post-hoc "
 "explanations should not carry the evidentiary weight of an interpretable model "
 "design [11]."),
("fig", "gradcam"),

("h1", "VI. LIMITATIONS"),
("p",
 "The following limitations are stated as scope conditions, not as future work."),
("bullets", [
 "<b>Single-corpus internal validation.</b> All reported numbers come from one "
 "institution's corpus and one patient-disjoint split. No external cohort, no "
 "cross-institution transport test and no temporal validation are reported, so the "
 "figures should be expected to be optimistic relative to deployment [13].",
 "<b>No confidence intervals or paired comparisons.</b> Patient-level bootstrap "
 "intervals and the paired bootstrap ablation specified in the protocol could not be "
 "computed because per-study predictions were not retained ({tab:T5}). Consequently no "
 "difference between this model and any other system, including its own ablation, is "
 "reported as statistically supported.",
 "<b>Small-event findings.</b> Pneumonia has six positive held-out studies. Its "
 "metrics are descriptive and unstable, and the macro average is dominated by this "
 "term.",
 "<b>Label noise of unknown magnitude.</b> Targets are report-derived; no "
 "radiologist-annotated subset was used to estimate the noise rate, and the "
 "direction of the resulting bias is argued rather than measured.",
 "<b>Subgroup performance not assessed.</b> No stratified analysis by sex, age band, "
 "view position or reported race/ethnicity is reported. Because the model consumes "
 "sex and age directly, subgroup performance cannot be assumed uniform [16]&ndash;[19].",
 "<b>Calibration not assessed.</b> No reliability diagram, expected calibration error "
 "or recalibration is reported, and the weighted objective biases the probabilities "
 "by construction [15].",
 "<b>No reader study.</b> No radiologist comparison, no time-to-decision measurement "
 "and no assessment of whether model output changes human performance are available "
 "[4].",
 "<b>No shortcut-control experiments.</b> The metadata-only control, the "
 "view-position permutation audit and the adversarial-invariance variant described in "
 "Section V-C were not run.",
 "<b>Explainability is unvalidated.</b> Grad-CAM is provided as a qualitative aid "
 "only; no localisation ground truth and no saliency sanity check are used [11].",
 "<b>Single training run.</b> One seed, eight completed epochs. No seed replication, "
 "no hyperparameter search and no variance estimate across runs are reported, so the "
 "sensitivity of the results to initialisation and data order is unknown.",
 "<b>Retrospective, de-identified secondary data.</b> The work uses a public "
 "de-identified research corpus with no prospective recruitment, no consent process "
 "and no regulatory review, and it is not a clinical trial of any kind.",
]),

("h1", "VII. REPRODUCIBILITY, ARTIFACT STATUS AND DATA AVAILABILITY"),
("p",
 "The framework is organised so that every reported number can be regenerated from "
 "three inputs: the metadata table, the image directory and the saved checkpoint. "
 "Training writes an interrupt-safe checkpoint that stores the model, optimiser and "
 "scheduler state together with the epoch index and the loss history; evaluation "
 "reloads that checkpoint, rebuilds the deterministic partition from the same seed "
 "and writes a structured metrics record. Repository policy excludes image data, "
 "checkpoints and generated outputs from version control, which means that a reader "
 "can inspect the code and the metric record but cannot re-execute the evaluation "
 "without supplying the corpus and the weights."),
("p",
 "The audit performed for this paper also identified four reporting gaps whose "
 "closure requires code changes rather than text changes, and these are listed here "
 "so that the gap is actionable rather than rhetorical. (i) The evaluation entry "
 "point should persist per-study identifiers, patient identifiers, labels and "
 "predicted probabilities, which is the single change that unlocks bootstrap "
 "intervals, subgroup tables, calibration curves and the paired ablation. (ii) The "
 "training loop should persist the raw training and validation loss series so that a "
 "loss figure can be drawn from the run itself. (iii) A metadata-only control "
 "checkpoint should be registered alongside the fused model. (iv) Evaluation should "
 "emit per-finding curve coordinates (false- and true-positive rates) so that "
 "reported ROC curves can be checked against reported AUCs without digitisation. In "
 "the present artifacts the first and fourth are exactly the gaps that prevented "
 "independent verification of the Cardiomegaly curve, discussed in Appendix B."),

("h1", "VIII. CONCLUSION"),
("p",
 "This paper reported MediVision AI, a multimodal DenseNet121 framework for "
 "multi-label chest radiograph classification, together with an explicit audit of "
 "what its artifacts do and do not support. On a patient-disjoint 830-study held-out "
 "partition the framework reached a macro AUC of 0.771, with the strongest "
 "discrimination for Pleural effusion (0.844) and Cardiomegaly (0.805) and the weakest, "
 "and least stable, for Pneumonia (0.709 on six positive studies). At a fixed "
 "threshold of 0.50 the model operated at macro sensitivity 0.638 and macro "
 "specificity 0.705."),
("p",
 "Those numbers are offered as a reproducible baseline, not as evidence of clinical "
 "readiness. The audit produced three findings that are more useful than the "
 "aggregate score. First, the class-weighted objective used in training cannot improve "
 "ranking metrics and should not be credited with improved discrimination; it shifts "
 "the operating point instead, which is visible in the per-finding sensitivity and "
 "specificity pairs. Second, the metadata channel is a plausible shortcut carrier "
 "because view position covaries with illness severity and acquisition setting, so "
 "the multimodal design requires a metadata-only control and a counterfactual "
 "permutation audit before any fusion benefit can be claimed. Third, the statistics "
 "promised by the original protocol&mdash;bootstrap intervals and a paired ablation "
 "&mdash;are not recoverable from the artifacts as released, and this version states "
 "that plainly rather than reporting estimates it cannot support."),
("p",
 "The immediate programme of work follows directly from these findings: persist "
 "per-study predictions, re-run evaluation to obtain patient-level bootstrap "
 "intervals, register image-only and metadata-only control checkpoints, complete the "
 "twenty-epoch budget with multiple seeds, and validate on a second institution's "
 "corpus. Until at least the first three of these are done, the framework should be "
 "described as a research prototype and used only for methodological study."),
]

# ----------------------------------------------------------------------------- tables
TABLES = {
"T1": dict(
 caption="Corpus and held-out composition. Split sizes are images; the nominal "
         "70/15/15 allocation is applied to patients, and the realized image "
         "fractions differ because studies per patient vary.",
 header=["Partition / finding", "Images", "Share", "Positives", "Prevalence"],
 rows=[
   ["Training", "3,447", "68.95%", "&mdash;", "&mdash;"],
   ["Validation", "722", "14.44%", "&mdash;", "&mdash;"],
   ["Test", "830", "16.60%", "643<super>a</super>", "&mdash;"],
   ["&nbsp;&nbsp;Normal", "830", "&mdash;", "451", "0.543"],
   ["&nbsp;&nbsp;Pneumonia", "830", "&mdash;", "6", "0.007"],
   ["&nbsp;&nbsp;Cardiomegaly", "830", "&mdash;", "73", "0.088"],
   ["&nbsp;&nbsp;Pleural effusion", "830", "&mdash;", "113", "0.136"],
   ["Total", "4,999", "100%", "&mdash;", "&mdash;"],
 ],
 note="<super>a</super> Positive label decisions summed across the four findings; the "
      "targets are not mutually exclusive, so this exceeds the number of studies. "
      "Per-finding positive counts for the training and validation partitions are not "
      "retained in the released metric record and are therefore not reported.",
),
"T2": dict(
 caption="Training configuration as read from the implementation, cross-checked "
         "against the manuscript (item F1&ndash;F3).",
 header=["Parameter", "Value", "Source of record"],
 rows=[
   ["Optimizer", "AdamW (&beta;<sub>1</sub> 0.9, &beta;<sub>2</sub> 0.999)", "code"],
   ["Learning rate", "1 &times; 10<super>&minus;4</super>", "code / config"],
   ["Weight decay", "1 &times; 10<super>&minus;4</super>", "code / config"],
   ["Batch size", "16", "code / config"],
   ["Epochs requested / completed", "20 / 8", "config / checkpoint"],
   ["Early-stopping patience", "5 epochs (validation loss)", "code / config"],
   ["LR schedule", "ReduceLROnPlateau (factor 0.5, patience 2)", "code"],
   ["Random seed", "42 (split, init, augmentation)", "code / config"],
   ["Patient-level split", "70 / 15 / 15", "code"],
   ["Input resolution", "224 &times; 224 &times; 3", "code / metadata"],
   ["Normalisation", "ImageNet mean and SD", "code"],
   ["Augmentation", "Affine &plusmn;5&deg;, translate 2%, scale 0.97&ndash;1.03; "
                    "h-flip p = 0.5", "code"],
   ["Dropout", "0.20 (metadata encoder, head)", "code"],
   ["Loss", "BCEWithLogits, pos_weight = N<sub>neg</sub>/N<sub>pos</sub>", "code"],
   ["Threshold", "0.50 (fixed, not tuned on test)", "code"],
 ],
 note="The completed-epoch count is read from the saved checkpoint record; the "
      "requested budget was 20 epochs and the patience criterion was never triggered.",
),
"T3": dict(
 caption="Held-out test performance at a fixed threshold of 0.50 (n = 830 studies). "
         "AUC is threshold-free; all other columns are computed at the fixed point.",
 header=["Finding", "Pos.", "AUC", "Sens.", "Spec.", "Prec.", "F1", "Acc."],
 rows=[
   ["Normal", "451", "0.724", "0.530", "0.792", "0.752", "0.622", "0.649"],
   ["Pneumonia", "6", "0.709", "0.667", "0.518", "0.010", "0.020", "0.519"],
   ["Cardiomegaly", "73", "0.805", "0.479", "0.863", "0.252", "0.330", "0.829"],
   ["Pleural effusion", "113", "0.844", "0.876", "0.646", "0.281", "0.425", "0.677"],
   ["<b>Macro (mean)</b>", "&mdash;", "<b>0.771</b>", "<b>0.638</b>", "<b>0.705</b>",
    "<b>0.323</b>", "<b>0.349</b>", "<b>0.669</b>"],
   ["Micro (pooled)", "643", "&mdash;", "0.586", "0.689", "0.311", "0.407", "&mdash;"],
 ],
 note="Precision for Pneumonia is 0.010 because only one of the roughly 400 positive "
      "predictions is correct; the value is reported for completeness and is not an "
      "usable operating characteristic. No confidence interval is reported for any "
      "cell ({tab:T5}).",
),
"T4": dict(
 caption="Confusion counts at threshold 0.50. Each matrix accounts for all 830 "
         "held-out studies; sensitivity and specificity in {tab:T3} are recomputable "
         "from these counts.",
 header=["Finding", "TN", "FP", "FN", "TP", "Sens.", "Spec."],
 rows=[
   ["Normal", "300", "79", "212", "239", "0.530", "0.792"],
   ["Pneumonia", "427", "397", "2", "4", "0.667", "0.518"],
   ["Cardiomegaly", "653", "104", "38", "35", "0.479", "0.863"],
   ["Pleural effusion", "463", "254", "14", "99", "0.876", "0.646"],
   ["<b>Micro (pooled)</b>", "<b>1,843</b>", "<b>834</b>", "<b>266</b>", "<b>377</b>",
    "<b>0.586</b>", "<b>0.689</b>"],
 ],
 note="Counts were read from the released metric record and independently re-derived; "
      "the row sums and the reported sensitivity and specificity agree exactly.",
),
"T5": dict(
 caption="Statistical analysis specified by the protocol, its status in this version, "
         "and the artifact change required to compute it.",
 header=["Estimand", "Status", "Blocker / requirement"],
 rows=[
   ["95% CI for macro AUC (patient-level resampling, 2,000 replicates)",
    "Not computed", "Per-study probabilities and patient IDs are discarded by the "
    "evaluation script"],
   ["95% CI for per-finding AUC", "Not computed", "Same as above"],
   ["95% CI for sensitivity / specificity at 0.50", "Not computed", "Same as above"],
   ["Paired bootstrap: fused vs image-only ablation", "Not computed; ablation not run",
    "Requires an image-only checkpoint trained on the identical partition, plus "
    "paired per-study predictions"],
   ["Subgroup metrics (sex, age band, view)", "Not computed",
    "Requires retained per-study metadata alongside predictions"],
   ["Calibration (reliability curve, ECE)", "Not computed",
    "Requires retained probabilities; ECE needs bin-wise counts"],
 ],
 note="Because the resampling unit cannot be reconstructed, no interval, standard "
      "error, p-value or paired difference is reported anywhere in this paper.",
),
}
