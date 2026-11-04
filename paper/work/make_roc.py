"""Figure 2: discrimination evidence.

The pipeline stores only aggregate metrics, so no per-study score vector and no
curve coordinates exist anywhere in the release. This figure therefore shows
exactly what is pinned down and nothing more.

Panel (a): the verified operating point of each finding, i.e. the single
          (FPR, TPR) pair implied by its count matrix at threshold 0.50, on one
          ROC grid. No curve is drawn, because the interior of a ROC curve is
          not identifiable from aggregate counts.

Panel (b): the recorded AUC of each finding (dot), its 95% Hanley-McNeil
          interval (bar), and the interval of AUC values attainable by any
          monotone ROC curve through that finding's verified operating point
          (open bracket, exact bounds from stats.py::auc_bracket).
"""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams.update({"font.family": "serif", "font.serif": ["DejaVu Serif"], "font.size": 8,
                 "axes.labelsize": 8, "axes.titlesize": 8, "legend.fontsize": 6.4,
                 "xtick.labelsize": 7, "ytick.labelsize": 7, "axes.linewidth": 0.7,
                 "axes.grid": True, "grid.linewidth": 0.35, "grid.alpha": 0.45,
                 "grid.linestyle": ":", "figure.dpi": 600, "savefig.bbox": "tight",
                 "savefig.pad_inches": 0.02})

S = json.load(open("stats.json"))
PF = S["per_finding"]
NM = {"Normal": "Normal", "Pneumonia": "Pneumonia",
      "Cardiomegaly": "Cardiomegaly", "Pleural_Effusion": "Pleural effusion"}
REL = ["Normal", "Cardiomegaly", "Pleural_Effusion"]
COL = {"Normal": "#1f4e79", "Cardiomegaly": "#7d3c98",
       "Pleural_Effusion": "#b9770e", "Pneumonia": "#c0392b"}

fig, axes = plt.subplots(1, 2, figsize=(6.9, 3.05),
                         gridspec_kw={"width_ratios": [1.0, 1.34]})

# ---------------------------------------------------------------- panel (a)
ax = axes[0]
ax.plot([0, 1], [0, 1], ls="--", lw=0.8, color="0.45", label="Chance (AUC 0.500)")
for k in REL:
    f, t = PF[k]["rates"]["fpr"], PF[k]["rates"]["tpr"]
    ax.plot([f], [t], marker="o", ms=6.2, mfc=COL[k], mec="white", mew=0.7,
            zorder=5, label=f"{NM[k]} (AUC {PF[k]['auc']:.3f})")
    ax.annotate(f"({f:.2f}, {t:.2f})", xy=(f, t), xytext=(6, -9),
                textcoords="offset points", fontsize=5.9, color=COL[k])
pk = "Pneumonia"
ax.plot([PF[pk]["rates"]["fpr"]], [PF[pk]["rates"]["tpr"]], marker="D", ms=4.6,
        mfc="white", mec=COL[pk], mew=1.1, zorder=5,
        label=f"Pneumonia, 6 positives (excluded)")
ax.set_xlim(0, 1); ax.set_ylim(0, 1.005)
ax.set_xlabel("False positive rate"); ax.set_ylabel("True positive rate")
ax.set_title("(a) Verified operating points at threshold 0.50", fontsize=7.5, pad=3)
ax.legend(loc="lower right", frameon=True, framealpha=0.95, borderpad=0.3,
          handlelength=1.4, labelspacing=0.3, fontsize=5.9)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)

# ---------------------------------------------------------------- panel (b)
ax = axes[1]
ys = np.arange(len(REL))[::-1]
ax.axvline(0.5, color="0.45", lw=0.8, ls="--")
ax.annotate("chance", xy=(0.503, len(REL) - 0.52), fontsize=5.8, color="0.45",
            rotation=90, va="top", ha="left")
for y, k in zip(ys, REL):
    lo, hi = PF[k]["auc_ci_hanley"]
    blo, bhi = PF[k]["auc_bracket"]
    ax.plot([blo, bhi], [y, y], lw=0.9, color="0.60", solid_capstyle="butt", zorder=1)
    ax.plot([blo, blo], [y - 0.12, y + 0.12], lw=0.9, color="0.42", zorder=1)
    ax.plot([bhi, bhi], [y - 0.12, y + 0.12], lw=0.9, color="0.42", zorder=1)
    ax.plot([lo, hi], [y, y], lw=5.4, color=COL[k], alpha=0.30,
            solid_capstyle="round", zorder=2)
    ax.plot([PF[k]["auc"]], [y], marker="o", ms=4.6, color=COL[k], zorder=5)
    ax.annotate(f"{PF[k]['auc']:.3f}  [{lo:.3f}, {hi:.3f}]", xy=(bhi + 0.012, y),
                fontsize=6.0, va="center", ha="left", color="0.12")
ax.set_xlim(0.35, 1.20); ax.set_ylim(-0.52, len(REL) - 0.48)
ax.set_yticks(ys)
ax.set_yticklabels([NM[k] for k in REL], fontsize=7)
ax.set_xticks([0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
ax.set_xlabel("Area under the ROC curve")
ax.set_title("(b) Recorded AUC: 95% interval and attainable range", fontsize=7.5, pad=3)
ax.grid(axis="y", visible=False)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
h1, = ax.plot([], [], lw=5.4, color="0.55", alpha=0.30)
h2, = ax.plot([], [], lw=0.9, color="0.42")
fig.legend([h1, h2],
           ["95% Hanley–McNeil interval around the recorded AUC",
            "range attainable by any ROC curve through the verified operating point"],
           loc="lower center", ncol=2, frameon=False, fontsize=5.9,
           bbox_to_anchor=(0.5, -0.035), handlelength=1.8, columnspacing=1.8)

fig.tight_layout(w_pad=1.4)
fig.savefig("/home/user/changes/paper/figures/fig_roc.png", dpi=600)
print("fig_roc.png written")
for k in REL:
    print(" ", k, "AUC %.4f HM[%.4f,%.4f] attainable[%.4f,%.4f]"
          % (PF[k]["auc"], *PF[k]["auc_ci_hanley"], *PF[k]["auc_bracket"]))
