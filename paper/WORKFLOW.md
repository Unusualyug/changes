# MediVision AI — IEEE paper build

Everything in this folder is generated from `work/` in one pass; nothing is hand-edited.

| File | What it is |
|---|---|
| `MediVision_AI_IEEE_Research_Final.pdf` | IEEE two-column paper (14 pp.) |
| `MediVision_AI_IEEE_Research_Final.docx` | Same manuscript, editable Word file |
| `figures/fig_roc.png` | (a) three verified ROC curves; (b) Cardiomegaly AUC bracket derived from verified counts |
| `figures/fig_confusion.png` | 2x2 confusion matrix per finding |
| `figures/fig_loss.png` | Explicit "no data" panel — no loss series exists in the release |
| `figures/fig_gradcam.png` | Grad-CAM layout placeholder (labelled as such) |
| `figures/fig_pipeline.png` | System/pipeline diagram |

## Rebuild

```bash
cd paper/work
python3 -m pip install reportlab python-docx matplotlib numpy scikit-learn pillow pymupdf

python3 extract4.py          # ROC curve coordinates from the committed evaluation PNG
python3 compute.py           # derived metrics + artifact integrity checks -> results.json
python3 audit.py             # operating-point + integration tests across the three records
python3 audit2.py            # confusion-figure agreement and AUC-bracket impossibility test
python3 make_roc.py          # fig_roc.png
python3 make_conf.py         # fig_confusion.png
python3 make_loss.py         # fig_loss.png
python3 make_gradcam.py      # fig_gradcam.png
python3 make_pipeline.py     # fig_pipeline.png

python3 build_pdf.py         # -> ../MediVision_AI_IEEE_Research_Final.pdf
python3 build_docx.py        # -> ../MediVision_AI_IEEE_Research_Final.docx
python3 qa.py                # placeholder scan, citation audit, number cross-check
```

`content.py` and `content2.py` hold the manuscript text, tables and figure
captions; `refs.py` holds the reference metadata. Figure and table numbers are
assigned automatically in order of first citation through the `{fig:key}` and
`{tab:key}` tokens, so inserting a float never breaks the numbering.

To replace the two placeholder panels, produce real images at
`figures/fig_loss.png` and `figures/fig_gradcam.png`, then re-run
`build_pdf.py` and `build_docx.py` only.

## Revision 3 additions

Derived statistics are now generated, not typed:

```bash
cd paper/work
python3 stats.py        # -> stats.json (intervals, attainable AUC ranges, macro means)
python3 make_roc.py     # -> figures/fig_roc.png
python3 make_conf.py    # -> figures/fig_confusion.png
python3 build_pdf.py    # -> MediVision_AI_IEEE_Research_Final.pdf
python3 build_docx.py   # -> MediVision_AI_IEEE_Research_Final.docx
```

`stats.py` reads `medivision-ai-ml/evaluation_results/evaluation.json` and emits
Clopper-Pearson and Hanley-McNeil intervals, the exact attainable-AUC bracket of
Eq. (7), and the all-finding and three-finding macro averages. `content.py` and
`content2.py` import `stats.json`, so editing a number in the source JSON and
re-running `stats.py` propagates to the text, tables and figures.

Both placeholder figures (`fig_loss.png`, `fig_gradcam.png`) were deleted in
revision 3; they are no longer part of the build.
