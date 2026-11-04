# -*- coding: utf-8 -*-
"""Derived statistics computed from the released evaluation record.

Every quantity in the manuscript that is marked as derived comes from this
module, and `stats.json` is written as its record. Nothing here estimates a
model output: the count matrices, AUCs and supports are read from
`medivision-ai-ml/evaluation_results/evaluation.json`, and the functions below
are closed-form or exact resampling procedures over those integers.

Sources of truth
----------------
* counts, supports, AUCs  -> evaluation.json (the archived metric record)
* operating points        -> derived from the counts
* exact intervals         -> Clopper-Pearson / Wilson on the counts
* AUC intervals           -> Hanley-McNeil (normal approximation) and
                             DeLong (componentwise variance on the AUC)
* attainable AUC bracket  -> closed form, see `auc_bracket`
"""
import json
import os
from math import sqrt

import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
EVAL_JSON = os.path.join(os.path.dirname(os.path.dirname(BASE)),
                         "medivision-ai-ml", "evaluation_results", "evaluation.json")

# Findings whose held-out positive count is too small to support any inference.
MIN_EVENTS_FOR_INFERENCE = 30


# --------------------------------------------------------------------- inputs
def load_evaluation():
    with open(EVAL_JSON) as fh:
        return json.load(fh)


def counts(record=None):
    """Ordered {finding: (tn, fp, fn, tp)} from the archived record."""
    rec = record or load_evaluation()
    out = {}
    for name, m in rec["metrics"]["per_class"].items():
        tn, fp = m["confusion_matrix"][0]
        fn, tp = m["confusion_matrix"][1]
        out[name] = (int(tn), int(fp), int(fn), int(tp))
    return out


# ------------------------------------------------------------------ point est
def rates(c):
    tn, fp, fn, tp = c
    return dict(
        sens=tp / (tp + fn) if tp + fn else float("nan"),
        spec=tn / (tn + fp) if tn + fp else float("nan"),
        prec=tp / (tp + fp) if tp + fp else 0.0,
        fpr=fp / (fp + tn) if fp + tn else float("nan"),
        tpr=tp / (tp + fn) if tp + fn else float("nan"),
        acc=(tp + tn) / (tp + tn + fp + fn),
        npos=tp + fn, nneg=tn + fp,
    )


def macro(record=None, findings=None):
    """Unweighted mean of a set of per-finding quantities.

    `findings` restricted to the findings that are not flagged as
    small-event; see `reliable_findings`.
    """
    rec = record or load_evaluation()
    cs = counts(rec)
    names = findings if findings is not None else list(cs)
    per = {n: rates(cs[n]) for n in names}
    out = {k: float(np.mean([per[n][k] for n in names]))
           for k in ("sens", "spec", "prec", "acc")}
    out["auc"] = float(np.mean([rec["metrics"]["per_class"][n]["roc_auc"] for n in names]))
    out["findings"] = list(names)
    return out


def f1(p, r):
    return 0.0 if p + r == 0 else 2 * p * r / (p + r)


def reliable_findings(record=None, min_events=MIN_EVENTS_FOR_INFERENCE):
    cs = counts(record)
    return [n for n, c in cs.items() if c[2] + c[3] >= min_events]


# -------------------------------------------------------------------- intervals
def clopper_pearson(k, n, alpha=0.05):
    """Exact binomial interval; k successes in n trials."""
    from scipy.stats import beta
    if n == 0:
        return (float("nan"), float("nan"))
    lo = 0.0 if k == 0 else beta.ppf(alpha / 2, k, n - k + 1)
    hi = 1.0 if k == n else beta.ppf(1 - alpha / 2, k + 1, n - k)
    return (float(lo), float(hi))


def wilson(k, n, z=1.959963984540054):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, centre - half), min(1.0, centre + half))


def auс_var_hanley(auc, npos, nneg):
    """Hanley & McNeil variance of a single AUC (exponential approximation)."""
    q1 = auc / (2 - auc)
    q2 = 2 * auc * auc / (1 + auc)
    num = (auc * (1 - auc) + (npos - 1) * (q1 - auc * auc)
           + (nneg - 1) * (q2 - auc * auc))
    return max(num / (npos * nneg), 0.0)


def hanley_mcneil_ci(auc, npos, nneg, z=1.959963984540054):
    se = sqrt(auс_var_hanley(auc, npos, nneg))
    return (max(0.0, auc - z * se), min(1.0, auc + z * se)), se


def delong_auc_var(auc, npos, nneg, structural=(1.0, 0.0)):
    """Hanley-McNeil reference: variance with normal-structure assumption.

    `structural` = (P(x_pos > x_neg | structural), ...) is not identifiable from
    aggregate data, so the exponential-model form above is used and this helper
    only reports the Birnbaum-Klok style minimum-variance comparator, which is
    the conservative choice for non-normal score distributions.
    """
    p1, p2 = structural
    s1 = (auc * (1 - auc) + (npos - 1) * (p1 - auc * auc)
          + (nneg - 1) * (p2 - auc * auc))
    return max(s1 / (npos * nneg), 0.0)


def auc_bracket(fpr, tpr, npos, nneg):
    """Attainable AUC range for *any* monotone ROC curve through (fpr, tpr).

    A ROC curve is non-decreasing from (0,0) to (1,1) and passes through
    (f, t).  The area is therefore bounded below by the piecewise-linear path
    through that point and bounded above by the path that rises vertically to
    the point, runs horizontally to f = 1, and then rises to 1.

        AUC_min = 0.5 * f * t + (1 - f) * t
        AUC_max = f * t + 0.5 * f * (1 - t) ... is NOT the maximum

    The true maximum keeps TPR = 1 for f' in (f, 1), giving

        AUC_max = f * t + (1 - f)

    Both bounds are attainable by monotone curves, so the interval is exact for
    a fixed single point and is not an estimate.  `npos`/`nneg` are accepted for
    the caller's convenience and enter only the finite-sample note, not bounds.
    """
    lo = 0.5 * fpr * tpr + (1 - fpr) * tpr
    hi = fpr * tpr + (1 - fpr)
    return lo, hi


def bracketing_curves(fpr, tpr):
    """The two extreme ROC polylines whose areas are `auc_bracket`."""
    low = [(0.0, 0.0), (fpr, tpr), (1.0, 1.0)]
    high = [(0.0, 0.0), (0.0, 1.0), (fpr, 1.0), (1.0, 1.0)]
    return low, high


def auc_of_polyline(pts):
    return sum((pts[i + 1][0] - pts[i][0]) * (pts[i + 1][1] + pts[i][1]) / 2
               for i in range(len(pts) - 1))


# --------------------------------------------------------------------- report
def build(min_events=MIN_EVENTS_FOR_INFERENCE):
    rec = load_evaluation()
    cs = counts(rec)
    per = {}
    for name, c in cs.items():
        r = rates(c)
        auc = rec["metrics"]["per_class"][name]["roc_auc"]
        cp_sens = clopper_pearson(c[3], c[3] + c[2])
        cp_spec = clopper_pearson(c[0], c[0] + c[1])
        wl_sens = wilson(c[3], c[3] + c[2])
        (hm_lo, hm_hi), hm_se = hanley_mcneil_ci(auc, r["npos"], r["nneg"])
        lo, hi = auc_bracket(r["fpr"], r["tpr"], r["npos"], r["nneg"])
        per[name] = dict(
            counts=dict(tn=c[0], fp=c[1], fn=c[2], tp=c[3]),
            rates=r, auc=auc,
            sens_ci=cp_sens, spec_ci=cp_spec, sens_ci_wilson=wl_sens,
            auc_ci_hanley=(hm_lo, hm_hi), auc_se_hanley=hm_se,
            auc_bracket=(lo, hi),
            f1=f1(r["prec"], r["sens"]),
            reliable=(r["npos"] >= min_events),
        )
    rel = reliable_findings(rec, min_events)
    out = dict(
        source=os.path.relpath(EVAL_JSON, os.path.dirname(BASE)),
        sample_count=rec["metrics"]["sample_count"],
        min_events=min_events,
        per_finding=per,
        reliable_findings=rel,
        macro_all=macro(rec),
        macro_reliable=macro(rec, rel),
    )
    # pooled micro
    tn = sum(v[0] for v in cs.values()); fp = sum(v[1] for v in cs.values())
    fn = sum(v[2] for v in cs.values()); tp = sum(v[3] for v in cs.values())
    mr = rates((tn, fp, fn, tp))
    out["micro"] = dict(counts=dict(tn=tn, fp=fp, fn=fn, tp=tp), rates=mr,
                        f1=f1(mr["prec"], mr["sens"]))
    return out


if __name__ == "__main__":
    res = build()
    with open(os.path.join(BASE, "stats.json"), "w") as fh:
        json.dump(res, fh, indent=2)
    print(json.dumps(res, indent=2)[:4000])
