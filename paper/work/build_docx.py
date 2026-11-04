# -*- coding: utf-8 -*-
"""Render the manuscript to an IEEE-formatted .docx (A4, 2 columns, 10 pt serif)."""
import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from PIL import Image as PILImage

import build_common as BC
from build_common import ALL_BODY, ALL_TABLES, FIGURES, FIGNUM, TABNUM, ROMAN
import refs

OUT = os.path.join(BC.OUTDIR, BC.OUTBASE + ".docx")
ENT = BC.ENT
SERIF = "Times New Roman"

def txt(s):
    s = BC.resolve_crossrefs(s)
    for k, v in ENT.items():
        s = s.replace(k, v)
    s = s.replace("&nbsp;", " ")
    return s

TOKEN = re.compile(r"</?(b|i|sub|sup|super|em|strong)>")

def add_runs(par, s, size=None, base_bold=False, base_italic=False):
    """Write inline markup into a docx paragraph as runs."""
    s = txt(s)
    bold, italic, sub, sup = base_bold, base_italic, False, False
    pos = 0
    def emit(text):
        if not text: return
        r = par.add_run(text)
        r.bold = bold; r.italic = italic
        r.font.name = SERIF
        if sub: r.font.subscript = True
        if sup: r.font.superscript = True
        if size: r.font.size = Pt(size)
    for m in TOKEN.finditer(s):
        emit(s[pos:m.start()])
        tag = m.group(1); closing = m.group(0).startswith("</")
        key = {"super": "sup", "em": "i", "strong": "b"}.get(tag, tag)
        if key == "b": bold = (not closing) or base_bold
        elif key == "i": italic = (not closing) or base_italic
        elif key == "sub": sub = not closing
        elif key == "sup": sup = not closing
        pos = m.end()
    emit(s[pos:])

def para(doc, s, size=10, bold=False, italic=False, align="just", first=0.0,
         space_before=0, space_after=0, left=0.0, keep=False):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.alignment = {"just": WD_ALIGN_PARAGRAPH.JUSTIFY, "center": WD_ALIGN_PARAGRAPH.CENTER,
                    "left": WD_ALIGN_PARAGRAPH.LEFT}[align]
    pf.first_line_indent = Cm(first)
    pf.left_indent = Cm(left)
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    pf.line_spacing = 1.0
    pf.widow_control = True
    if keep: pf.keep_with_next = True
    add_runs(p, s, size=size, base_bold=bold, base_italic=italic)
    return p


def set_cols(sec, num, space=None):
    """Insert/replace w:cols in schema-correct position (before w:docGrid)."""
    sectPr = sec._sectPr
    for old in sectPr.findall(qn("w:cols")):
        sectPr.remove(old)
    cols = OxmlElement("w:cols")
    cols.set(qn("w:num"), str(num))
    if space:
        cols.set(qn("w:space"), str(space))
    anchor = None
    for tag in ("w:docGrid", "w:printerSettings", "w:sectPrChange", "w:titlePg",
                "w:textDirection", "w:bidi", "w:rtlGutter", "w:vAlign", "w:formProt"):
        el = sectPr.find(qn(tag))
        if el is not None:
            anchor = el
            break
    if anchor is not None:
        anchor.addprevious(cols)
    else:
        sectPr.append(cols)

def shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hexcolor)
    tcPr.append(shd)

def set_borders(table, rows_spec):
    tbl = table._tbl
    tblPr = tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement("w:" + edge)
        if edge in ("top", "bottom"):
            el.set(qn("w:val"), "single"); el.set(qn("w:sz"), "10")
        elif edge == "left" or edge == "right":
            el.set(qn("w:val"), "none")
        else:
            el.set(qn("w:val"), "none")
        el.set(qn("w:space"), "0"); el.set(qn("w:color"), "000000")
        borders.append(el)
    tblPr.append(borders)

def add_table(doc, key, avail_cm):
    t = ALL_TABLES[key]
    n = TABNUM[key]
    cap = doc.add_paragraph()
    cap.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    cap.paragraph_format.space_before = Pt(6)
    cap.paragraph_format.space_after = Pt(3)
    cap.paragraph_format.keep_with_next = True
    r = cap.add_run("TABLE %s" % ROMAN[n]); r.bold = True; r.font.size = Pt(9)
    r.font.name = SERIF
    cap.add_run().add_break()
    add_runs(cap, t["caption"], size=9)
    nc = len(t["header"])
    tbl = doc.add_table(rows=1 + len(t["rows"]), cols=nc)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = True
    set_borders(tbl, None)
    for j, h in enumerate(t["header"]):
        cell = tbl.rows[0].cells[j]
        cell.text = ""
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(2); p.paragraph_format.space_after = Pt(2)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_runs(p, h, size=8, base_bold=True)
    for i, row in enumerate(t["rows"], start=1):
        for j, c in enumerate(row):
            cell = tbl.rows[i].cells[j]
            cell.text = ""
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(1.5); p.paragraph_format.space_after = Pt(1.5)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.CENTER
            add_runs(p, c, size=8)
            if i % 2 == 0:
                shade(cell, "F4F6F9")
    if t.get("note"):
        nt = doc.add_paragraph()
        nt.paragraph_format.space_before = Pt(2)
        nt.paragraph_format.space_after = Pt(4)
        nt.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        add_runs(nt, "<i>Note:</i> " + t["note"], size=8)

def add_figure(doc, key, avail_cm, max_h_cm):
    cfg = FIGURES[key]
    path = os.path.join(BC.FIGDIR, cfg["file"])
    iw, ih = PILImage.open(path).size
    w = avail_cm
    h = w * ih / iw
    if h > max_h_cm:
        h = max_h_cm; w = h * iw / ih
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(path, width=Cm(w), height=Cm(h))
    cap = doc.add_paragraph()
    cap.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    cap.paragraph_format.space_after = Pt(6)
    r = cap.add_run("Fig. %d. " % FIGNUM[key]); r.bold = True; r.font.size = Pt(8.5)
    r.font.name = SERIF
    add_runs(cap, cfg["caption"], size=8.5)

def build():
    doc = Document()
    # base style
    st = doc.styles["Normal"]
    st.font.name = SERIF
    st.font.size = Pt(10)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), SERIF)
    st.paragraph_format.space_after = Pt(0)
    st.paragraph_format.line_spacing = 1.0

    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    sec.left_margin = sec.right_margin = Cm(1.27)
    sec.top_margin = Cm(1.9); sec.bottom_margin = Cm(1.9)
    avail_full = 21.0 - 2 * 1.27

    # ---- title block (outside the columns) in the first section, one column
    set_cols(doc.sections[0], 1)

    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(10)
    add_runs(p, BC.TITLE, size=20)

    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(2)
    add_runs(p, BC.AUTHORS, size=11)

    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(10)
    add_runs(p, BC.AFFIL.replace("<br/>", " | "), size=9, base_italic=True)

    # abstract + index terms, full width
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_after = Pt(6)
    add_runs(p, "<b><i>Abstract</i>&mdash;</b>" + BC.ABSTRACT, size=9.5)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_after = Pt(10)
    add_runs(p, "<b><i>Index Terms</i>&mdash;</b>" + BC.KEYWORDS, size=9.5)

    # ---- new section: two columns for the body
    new_sec = doc.add_section(WD_SECTION.CONTINUOUS)
    new_sec.page_width, new_sec.page_height = Cm(21.0), Cm(29.7)
    new_sec.left_margin = new_sec.right_margin = Cm(1.27)
    new_sec.top_margin = Cm(1.9); new_sec.bottom_margin = Cm(1.9)
    set_cols(new_sec, 2, 340)     # 0.6 cm gutter
    avail_col = (avail_full - 0.6) / 2.0

    pending_full = []   # full-width blocks collected in order

    def emit_full(kind, payload):
        # open a one-column continuous section, emit, then reopen two columns
        s = doc.add_section(WD_SECTION.CONTINUOUS)
        s.page_width, s.page_height = Cm(21.0), Cm(29.7)
        s.left_margin = s.right_margin = Cm(1.27)
        s.top_margin = Cm(1.9); s.bottom_margin = Cm(1.9)
        set_cols(s, 1)
        if kind == "table":
            add_table(doc, payload, avail_full)
        else:
            add_figure(doc, payload, avail_full, 9.4)
        s2 = doc.add_section(WD_SECTION.CONTINUOUS)
        s2.page_width, s2.page_height = Cm(21.0), Cm(29.7)
        s2.left_margin = s2.right_margin = Cm(1.27)
        s2.top_margin = Cm(1.9); s2.bottom_margin = Cm(1.9)
        set_cols(s2, 2, 340)

    for kind, payload in ALL_BODY:
        if kind == "h1":
            para(doc, payload, size=10, align="center", space_before=10, space_after=5, keep=True)
        elif kind == "h2":
            para(doc, payload, size=10, align="left", space_before=7, space_after=3,
                 italic=True, keep=True)
        elif kind == "p":
            para(doc, payload, size=10, first=0.5)
        elif kind == "eq":
            lines, num = payload
            for k, ln in enumerate(lines):
                p = doc.add_paragraph()
                p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_before = Pt(4 if k == 0 else 0)
                p.paragraph_format.space_after = Pt(4)
                add_runs(p, ln, size=9.5)
                if k == (len(lines) - 1) // 2:
                    p.add_run("\t\t(%s)" % num).font.size = Pt(9.5)
        elif kind == "bullets":
            for b in payload:
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Cm(0.55)
                p.paragraph_format.first_line_indent = Cm(-0.3)
                p.paragraph_format.space_after = Pt(3)
                p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                r = p.add_run("\u2022  "); r.font.size = Pt(10); r.font.name = SERIF
                add_runs(p, b, size=10)
        elif kind in ("fig", "table"):
            emit_full(kind, payload)

    para(doc, "REFERENCES", size=10, align="center", space_before=12, space_after=5, keep=True)
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
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(0.7)
        p.paragraph_format.first_line_indent = Cm(-0.7)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        add_runs(p, s, size=8)
        if r.get("note"):
            p2 = doc.add_paragraph()
            p2.paragraph_format.left_indent = Cm(0.7)
            p2.paragraph_format.space_after = Pt(3)
            p2.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            add_runs(p2, "Note: " + r["note"], size=7.5, base_italic=True)

    # page number footer
    footer = doc.sections[-1].footer
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = fp.add_run()
    fld = OxmlElement("w:fldSimple"); fld.set(qn("w:instr"), "PAGE")
    run._r.addnext(fld)
    fp.add_run("").font.size = Pt(8)

    doc.core_properties.title = "MediVision AI — IEEE research paper"
    doc.core_properties.author = "Y. Lakhani"
    doc.core_properties.subject = "Multi-label chest radiograph classification"
    doc.save(OUT)
    print("DOCX written:", OUT)

if __name__ == "__main__":
    build()
