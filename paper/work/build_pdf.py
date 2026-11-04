# -*- coding: utf-8 -*-
"""Render the manuscript to an IEEE-style two-column PDF using ReportLab."""
import os, sys, re, copy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, Image, Table, TableStyle, KeepTogether,
                                NextPageTemplate, PageBreak, FrameBreak, Flowable)
import matplotlib, os as _os

import build_common as BC
from build_common import ALL_BODY, ALL_TABLES, FIGURES, FIGNUM, TABNUM, ROMAN
import refs

# ------------------------------------------------------------------ fonts
FONTDIR = _os.path.join(_os.path.dirname(matplotlib.__file__), "mpl-data", "fonts", "ttf")
pdfmetrics.registerFont(TTFont("Serif", _os.path.join(FONTDIR, "DejaVuSerif.ttf")))
pdfmetrics.registerFont(TTFont("Serif-Bold", _os.path.join(FONTDIR, "DejaVuSerif-Bold.ttf")))
pdfmetrics.registerFont(TTFont("Serif-Italic", _os.path.join(FONTDIR, "DejaVuSerif-Italic.ttf")))
pdfmetrics.registerFont(TTFont("Serif-BoldItalic", _os.path.join(FONTDIR, "DejaVuSerif-BoldItalic.ttf")))
pdfmetrics.registerFontFamily("Serif", normal="Serif", bold="Serif-Bold",
                              italic="Serif-Italic", boldItalic="Serif-BoldItalic")

# Unicode entities: do NOT map &nbsp; to a space here (it is handled per-context)
ENT = {k: v for k, v in BC.ENT.items() if k != "&nbsp;"}

def rich(s, nbsp="\u00a0"):
    """Inline markup -> ReportLab intra-paragraph markup."""
    s = s.replace("&nbsp;", nbsp)
    for k, v in ENT.items():
        s = s.replace(k, v)
    s = s.replace("<sup>", "<super>").replace("</sup>", "</super>")
    s = s.replace("<em>", "<i>").replace("</em>", "</i>")
    s = s.replace("<strong>", "<b>").replace("</strong>", "</b>")
    s = s.replace("<super>", "\x01").replace("</super>", "\x02")
    s = s.replace("<sub>", "\x03").replace("</sub>", "\x04")
    s = s.replace("&", "&amp;")            # escape stray ampersands
    s = s.replace("\x01", "<super>").replace("\x02", "</super>")
    s = s.replace("\x03", "<sub>").replace("\x04", "</sub>")
    return s

def resolve(s):
    s = BC.resolve_crossrefs(s)
    return s

# ------------------------------------------------------------------ styles
JUST = TA_JUSTIFY
S = {}
S["title"] = ParagraphStyle("title", fontName="Serif", fontSize=17.5, leading=21.5,
                            alignment=TA_CENTER, spaceAfter=9, spaceBefore=0)
S["authors"] = ParagraphStyle("authors", fontName="Serif", fontSize=11, leading=14.5,
                              alignment=TA_CENTER, spaceAfter=2)
S["affil"] = ParagraphStyle("affil", fontName="Serif-Italic", fontSize=8.6, leading=11,
                            alignment=TA_CENTER, spaceAfter=9, textColor=colors.HexColor("#1a1a1a"))
S["abstract"] = ParagraphStyle("abstract", fontName="Serif-Bold", fontSize=8.5, leading=10.6,
                               alignment=JUST, firstLineIndent=0, spaceAfter=4,
                               leftIndent=16, rightIndent=16)
S["keywords"] = ParagraphStyle("keywords", fontName="Serif", fontSize=8.5, leading=10.6,
                               alignment=JUST, leftIndent=16, rightIndent=16, spaceAfter=2)
S["h1"] = ParagraphStyle("h1", fontName="Serif", fontSize=9.6, leading=12, alignment=TA_CENTER,
                         spaceBefore=9, spaceAfter=4.5, textColor=colors.HexColor("#111111"))
S["h2"] = ParagraphStyle("h2", fontName="Serif-Italic", fontSize=9.6, leading=12,
                         alignment=TA_LEFT, spaceBefore=6.5, spaceAfter=2.6,
                         firstLineIndent=0)
S["body"] = ParagraphStyle("body", fontName="Serif", fontSize=9.2, leading=11.6,
                           alignment=JUST, firstLineIndent=12, spaceAfter=0)
S["bullet"] = ParagraphStyle("bullet", parent=S["body"], firstLineIndent=0,
                             leftIndent=13, bulletIndent=3, spaceAfter=2.6,
                             bulletFontName="Serif", bulletFontSize=8)
S["eq"] = ParagraphStyle("eq", fontName="Serif", fontSize=8.5, leading=12.0,
                         alignment=TA_CENTER, spaceBefore=3, spaceAfter=3)
S["caption"] = ParagraphStyle("caption", fontName="Serif", fontSize=8.2, leading=10.4,
                              alignment=JUST, spaceBefore=3, spaceAfter=2)
S["tablecap"] = ParagraphStyle("tablecap", fontName="Serif", fontSize=8.2, leading=10.4,
                               alignment=JUST, spaceAfter=3.5)
S["tcell"] = ParagraphStyle("tcell", fontName="Serif", fontSize=7.3, leading=9,
                            alignment=TA_LEFT)
S["tcellc"] = ParagraphStyle("tcellc", parent=S["tcell"], alignment=TA_CENTER)
S["theadc"] = ParagraphStyle("theadc", fontName="Serif-Bold", fontSize=7.3, leading=9,
                             alignment=TA_CENTER, spaceBefore=0, spaceAfter=0)
S["thead"] = ParagraphStyle("thead", fontName="Serif-Bold", fontSize=7.3, leading=9,
                            alignment=TA_CENTER)
S["note"] = ParagraphStyle("note", fontName="Serif", fontSize=7.3, leading=8.9,
                           alignment=JUST, spaceBefore=2)
S["ref"] = ParagraphStyle("ref", fontName="Serif", fontSize=7.55, leading=9.1,
                          alignment=JUST, leftIndent=13, firstLineIndent=-13, spaceAfter=1.1)
S["refnote"] = ParagraphStyle("refnote", parent=S["ref"], fontName="Serif-Italic",
                              textColor=colors.HexColor("#444444"))

# ------------------------------------------------------------------ geometry
PW, PH = A4
LM = RM = 45.0
TM, BM = 52.0, 56.0
GAP = 15.0
CW = (PW - LM - RM - GAP) / 2.0          # column width
FULLW = PW - LM - RM                      # full text width
BODY_H = PH - TM - BM

# ------------------------------------------------------------------ wide-float machinery
class TopFloat(Flowable):
    """A block that must occupy the full text width at the top of a page."""
    def __init__(self, flowable, key):
        Flowable.__init__(self)
        self.f = flowable
        self.key = key
        self.h = 0
    def width(self):
        return FULLW
    def wrap(self, aw, ah):
        w, h = self.f.wrap(FULLW, BODY_H)
        self.h = h
        self._w = w
        return (FULLW, h)
    def draw(self):
        self.f.drawOn(self.canv, 0, 0)


class Paper(BaseDocTemplate):
    def __init__(self, fn, **kw):
        BaseDocTemplate.__init__(self, fn, pagesize=A4, leftMargin=LM, rightMargin=RM,
                                 topMargin=TM, bottomMargin=BM,
                                 title="MediVision AI — IEEE research paper",
                                 author="Y. Lakhani", **kw)
        self.pending_float = None
        self.page_of_template = {}

    def afterInit(self):
        BaseDocTemplate.afterInit(self)

    def make_templates(self, float_heights, front_height):
        two = PageTemplate(id="two", frames=[
            Frame(LM, BM, CW, BODY_H, id="l", leftPadding=0, rightPadding=0,
                  topPadding=0, bottomPadding=0),
            Frame(LM + CW + GAP, BM, CW, BODY_H, id="r", leftPadding=0, rightPadding=0,
                  topPadding=0, bottomPadding=0)],
            onPage=self._deco)
        tpls = []
        # page 1: front matter block then two columns
        tpls.append(PageTemplate(id="front", frames=[
            Frame(LM, BM + BODY_H - front_height, FULLW, front_height, id="top",
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0),
            Frame(LM, BM, CW, BODY_H - front_height - 6, id="l",
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0),
            Frame(LM + CW + GAP, BM, CW, BODY_H - front_height - 6, id="r",
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)],
            onPage=self._deco))
        tpls.append(two)
        for key, h in float_heights.items():
            if key.startswith("multifloat_"):
                # a float page holds only its floats: one full-height frame
                tpls.append(PageTemplate(id=key, frames=[
                    Frame(LM, BM, FULLW, BODY_H, id="top",
                          leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)],
                    onPage=self._deco))
                continue
            hid = "wide_" + key
            tpls.append(PageTemplate(id=hid, frames=[
                Frame(LM, BM + BODY_H - h, FULLW, h, id="top",
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0),
                Frame(LM, BM, CW, BODY_H - h - 6, id="l",
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0),
                Frame(LM + CW + GAP, BM, CW, BODY_H - h - 6, id="r",
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)],
                onPage=self._deco))
        self.addPageTemplates(tpls)

    def _deco(self, canv, doc):
        canv.saveState()
        canv.setFont("Serif", 7.6)
        canv.setFillColor(colors.HexColor("#555555"))
        canv.drawCentredString(PW / 2.0, 26, str(doc.page))
        canv.restoreState()

# ------------------------------------------------------------------ builders
# Floats that need more width than a single column are set full-width at the top
# of a page, which is standard IEEE practice for wide tables.
WIDE = {"tab_T6"}

def key_of(kind, payload):
    return ("tab_" if kind == "table" else "fig_") + payload

def is_wide(kind, payload):
    return key_of(kind, payload) in WIDE
def mk_image(path, max_h=None, width=FULLW):
    from PIL import Image as PILImage
    iw, ih = PILImage.open(path).size
    w = width
    h = w * ih / iw
    if max_h and h > max_h:
        h = max_h
        w = h * iw / ih
    img = Image(path, width=w, height=h)
    img.hAlign = "CENTER"
    return img, h

def fig_block(key, width=FULLW):
    cfg = FIGURES[key]
    path = os.path.join(BC.FIGDIR, cfg["file"])
    img, h = mk_image(path, max_h=(3.15 if width > 300 else 2.55) * inch, width=width)
    n = FIGNUM[key]
    cap = Paragraph("<b>Fig. %d.</b> %s" % (n, rich(resolve(cfg["caption"]))), S["caption"])
    return [img, Spacer(1, 2.5), cap], h + 2.5 + 3

def table_block(key, width=FULLW):
    t = ALL_TABLES[key]
    n = TABNUM[key]
    nc = len(t["header"])
    hdr = [Paragraph(rich(c), S["theadc"]) for c in t["header"]]
    rows = [[Paragraph(rich(resolve(c)), S["tcellc"] if i else S["tcell"])
             for i, c in enumerate(r)] for r in t["rows"]]
    # proportional widths from character counts
    # Column widths: a proportional estimate, then a water-filling pass that
    # guarantees each column can hold its longest unbreakable token.
    lengths = []
    for j in range(nc):
        m = max(len(BC.plain(t["header"][j])), 3)
        for r in t["rows"]:
            m = max(m, min(46, len(BC.plain(r[j]))))
        lengths.append(m)
    tot = float(sum(lengths))
    cw = [width * l / tot for l in lengths]
    # Exact needs: the widest unbreakable word in each column, measured with the
    # same font metrics ReportLab will use, plus the cell padding.
    PADX = 6.0
    need = []
    for j in range(nc):
        wmax = 0.0
        for cell, fnt in [(t["header"][j], "Serif-Bold")] + \
                         [(r[j], "Serif") for r in t["rows"]]:
            for tok in BC.plain(cell).split("/"):
                wmax = max(wmax, pdfmetrics.stringWidth(tok, fnt, 7.3) + PADX + 0.6)
        need.append(wmax)
    # The label column may wrap on spaces (a two-line finding name is normal in
    # IEEE tables); every other column must hold its widest cell intact.
    need[0] = min(need[0], 0.86 * inch)
    for j in range(1, nc):
        need[j] += 1.0
    # never let the requirements exceed the frame: cap wide columns first
    excess = sum(need) - width
    if excess > 0:
        wide = [j for j in range(nc) if need[j] > width / nc]
        for j in sorted(wide, key=lambda k: -need[k]):
            if excess <= 0:
                break
            take = min(excess, need[j] - width / nc)
            need[j] -= take
            excess -= take
        if excess > 0:
            for j in range(nc):
                need[j] = max(need[j] - excess / nc, 0.30 * inch)
    total_need = sum(need)
    if total_need < width:
        # distribute the slack in proportion to each column's requirement
        cw = [n * width / total_need for n in need]
    else:
        cw = list(need)
        scale = width / total_need
        cw = [c * scale for c in cw]
    if t.get("widths"):
        wts = [float(x) for x in t["widths"]]
        cw = [width * w / sum(wts) for w in wts]
    data = [hdr] + rows
    tbl = Table(data, colWidths=cw, repeatRows=1, hAlign="CENTER")
    style = [
        ("FONTNAME", (0, 0), (-1, -1), "Serif"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.4),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("LINEABOVE", (0, 0), (-1, 0), 0.9, colors.black),
        ("LINEBELOW", (0, 0), (-1, 0), 0.55, colors.black),
        ("LINEBELOW", (0, -1), (-1, -1), 0.9, colors.black),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f6f9")]),
    ]
    tbl.setStyle(TableStyle(style))
    cap = Paragraph("<b>TABLE %s</b><br/>%s" % (ROMAN[n], rich(resolve(t["caption"]))),
                    S["tablecap"])
    block = [cap, tbl]
    if t.get("note"):
        block += [Spacer(1, 2), Paragraph(rich("<i>Note:</i> " + resolve(t["note"])), S["note"])]
    _, th = tbl.wrap(width, BODY_H)
    ch = cap.wrap(width, BODY_H)[1]
    nh = 0
    if t.get("note"):
        nh = Paragraph(rich("<i>Note:</i> " + resolve(t["note"])), S["note"]).wrap(width, BODY_H)[1] + 2
    return block, th + ch + nh + 6

def ref_paragraphs():
    out = []
    for i, k in enumerate(list(refs.REFS.keys()), 1):
        r = refs.REFS[k]
        s = "[%d] %s, &ldquo;%s,&rdquo; " % (i, r["a"], r["t"])
        if r.get("v"):
            s += "<i>%s</i>" % r["v"]
            if r.get("vol"): s += ", vol. %s" % r["vol"]
            if r.get("no"): s += ", no. %s" % r["no"]
            if r.get("pp"): s += ", pp. %s" % r["pp"]
            s += ", %s" % r["y"]
        else:
            s += ", %s" % r["y"]
        s += ". doi: %s." % r["doi"]
        out.append(Paragraph(rich(s), S["ref"]))
        if r.get("note"):
            out.append(Paragraph(rich("Note: " + r["note"]), S["refnote"]))
    return out

# ------------------------------------------------------------------ assemble
def build():
    # measure floats first so that page templates can be sized
    heights = {}
    blocks = {}
    doc_extra = {}
    pending = {}
    for kind, payload in ALL_BODY:
        if kind not in ("fig", "table"):
            continue
        w = FULLW if is_wide(kind, payload) else CW
        if kind == "fig":
            blk, h = fig_block(payload, width=w)
        elif kind == "table":
            blk, h = table_block(payload, width=w)
        else:
            continue
        key = ("fig_" if kind == "fig" else "tab_") + payload
        blocks[key] = blk; heights[key] = h

    story = []
    # ---- front matter (full width block on page 1)
    front = []
    front.append(Paragraph(rich(BC.TITLE), S["title"]))
    front.append(Paragraph(rich(BC.AUTHORS), S["authors"]))
    front.append(Paragraph(rich(BC.AFFIL), S["affil"]))
    front.append(Paragraph(rich("<b><i>Abstract</i>&mdash;</b>" + BC.ABSTRACT), S["abstract"]))
    front.append(Paragraph(rich("<b><i>Index Terms</i>&mdash;</b>" + BC.KEYWORDS), S["keywords"]))
    fh = 0
    for f in front:
        fh += f.wrap(FULLW, BODY_H)[1]
        fh += f.getSpaceBefore() + f.getSpaceAfter()
    fh += 14

    body_story = []
    items = list(ALL_BODY)
    floats = [it for it in items if it[0] in ("fig", "table") and is_wide(it[0], it[1])]
    # (a) wide floats are hoisted to the next page; (b) at most two to a page
    groups, cur, curh = [], [], 0.0
    for kind, payload in floats:
        key = ("fig_" if kind == "fig" else "tab_") + payload
        if cur and (len(cur) >= 2 or curh + heights[key] + 14 > BODY_H):
            groups.append(cur); cur, curh = [], 0.0
        cur.append((kind, payload, key)); curh += heights[key] + 14
    if cur: groups.append(cur)
    for gi, g in enumerate(groups):
        tid = "multifloat_%d" % gi
        doc_extra[tid] = sum(heights[k] + 14 for _, _, k in g)
        pending[tid] = g

    key2gid = {k: t for t, g in pending.items() for _, _, k in g}
    used, i = set(), 0
    while i < len(items):
        kind, payload = items[i]
        if kind in ("fig", "table"):
            key0 = key_of(kind, payload)
            if not is_wide(kind, payload) or key2gid.get(key0) in used:
                key = key0
                blk = blocks[key]
                body_story.append(Spacer(1, 5))
                if kind == "table":
                    body_story.append(KeepTogether(blk[:-1]))
                    if len(blk) > 1:
                        body_story.append(blk[-1])
                else:
                    body_story.append(KeepTogether(blk))
                body_story.append(Spacer(1, 5))
                i += 1
                continue
        if kind in ("fig", "table"):
            key = ("fig_" if kind == "fig" else "tab_") + payload
            gid = key2gid[key]
            if gid in used:
                i += 1
                continue
            used.add(gid)
            body_story.append(NextPageTemplate("multifloat_%d" % int(gid.split("_")[1])))
            body_story.append(PageBreak())
            for n, (k2, p2, key2) in enumerate(pending[gid]):
                blk = blocks[key2]
                body_story.append(TopFloat(blk[0], key2))
                for f in blk[1:]:
                    body_story.append(f)
                if n < len(pending[gid]) - 1:
                    body_story.append(Spacer(1, 12))
            body_story.append(PageBreak())
            body_story.append(NextPageTemplate("two"))
            i += 1
            continue
        if kind == "h1":
            body_story.append(Paragraph(rich(payload), S["h1"]))
        elif kind == "h2":
            body_story.append(Paragraph(rich(payload), S["h2"]))
        elif kind == "p":
            body_story.append(Paragraph(rich(resolve(payload)), S["body"]))
        elif kind == "eq":
            lines, num = payload
            nrow = len(lines)
            numrow = (nrow - 1) // 2
            data = []
            for r, ln in enumerate(lines):
                data.append([Paragraph(rich(ln), S["eq"]),
                             Paragraph("(%s)" % num if r == numrow else "", S["eq"])])
            tbl = Table(data, colWidths=[CW - 20, 20])
            tbl.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                     ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                     ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                                     ("TOPPADDING", (0, 0), (-1, -1), 3),
                                     ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
            body_story.append(tbl)
        elif kind == "bullets":
            for btxt in payload:
                body_story.append(Paragraph(rich(resolve(btxt)), S["bullet"],
                                            bulletText="\u2022"))
        i += 1

    body_story.append(Paragraph(rich("REFERENCES"), S["h1"]))
    body_story.extend(ref_paragraphs())

    doc = Paper(os.path.join(BC.OUTDIR, BC.OUTBASE + ".pdf"))
    allh = dict(heights); allh.update(doc_extra)
    doc.make_templates(allh, fh + 26)
    doc.build([NextPageTemplate("two")] + front + body_story)
    print("PDF written:", os.path.join(BC.OUTDIR, BC.OUTBASE + ".pdf"))
    return heights

if __name__ == "__main__":
    build()
