# -*- coding: utf-8 -*-
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content import TITLE, AUTHORS, AFFIL, ABSTRACT, KEYWORDS, BODY, TABLES
from content2 import EXTRA_BODY, TABLES2, FIGURES
import refs

ALL_BODY = BODY + [("h1", "&nbsp;")] + EXTRA_BODY
ALL_TABLES = dict(TABLES); ALL_TABLES.update(TABLES2)

BASE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.join(os.path.dirname(BASE), "figures")
OUTDIR = os.path.join(os.path.dirname(BASE))
OUTBASE = "MediVision_AI_IEEE_Research_Final"

# ---------------------------------------------------------------- numbering
# Figures/tables are numbered in order of first appearance in the body.
fig_order, tab_order = [], []
for kind, payload in ALL_BODY:
    if kind == "fig" and payload not in fig_order: fig_order.append(payload)
    if kind == "table" and payload not in tab_order: tab_order.append(payload)
FIGNUM = {k: i + 1 for i, k in enumerate(fig_order)}
TABNUM = {k: i + 1 for i, k in enumerate(tab_order)}
ROMAN = {1:"I",2:"II",3:"III",4:"IV",5:"V",6:"VI",7:"VII",8:"VIII",9:"IX",10:"X"}

# The prose refers to figures/tables by these placeholder tokens.
CROSSREF = {}
for k, n in FIGNUM.items(): CROSSREF["{fig:%s}" % k] = "Fig.&nbsp;%d" % n
for k, n in TABNUM.items():
    CROSSREF["{tab:%s}" % k] = ("Table&nbsp;%s" % ROMAN[n]) if n <= 10 else ("Table&nbsp;%d" % n)

def resolve_crossrefs(text):
    for k, v in CROSSREF.items(): text = text.replace(k, v)
    return text

# ------------------------------------------------------------------ tokens
def tokens(s):
    """Split an inline-markup string into (text, style) runs.
    style keys: b, i, sub, sup."""
    out, stack = [], {}
    pat = re.compile(r"</?(b|i|sub|sup|super|em|strong)>")
    pos = 0
    for m in pat.finditer(s):
        if m.start() > pos:
            out.append((s[pos:m.start()], dict(stack)))
        tag = m.group(1); closing = m.group(0).startswith("</")
        key = {"super":"sup","em":"i","strong":"b"}.get(tag, tag)
        if closing: stack.pop(key, None)
        else: stack[key] = True
        pos = m.end()
    if pos < len(s): out.append((s[pos:], dict(stack)))
    return [r for r in out if r[0] != ""]

def plain(s):
    return re.sub(r"</?(b|i|sub|sup|super|em|strong)>", "", s).replace("&nbsp;", " ")

ENT = {"&ndash;":"\u2013","&mdash;":"\u2014","&times;":"\u00d7","&plusmn;":"\u00b1",
       "&deg;":"\u00b0","&mu;":"\u03bc","&sigma;":"\u03c3","&Sigma;":"\u03a3",
       "&phi;":"\u03c6","&theta;":"\u03b8","&sigma;":"\u03c3","&isin;":"\u2208",
       "&le;":"\u2264","&ge;":"\u2265","&minus;":"\u2212","&middot;":"\u00b7",
       "&alpha;":"\u03b1","&beta;":"\u03b2","&nbsp;":" ","&amp;":"&","&lt;":"<",
       "&gt;":">","&rsquo;":"\u2019","&lsquo;":"\u2018","&ldquo;":"\u201c",
       "&rdquo;":"\u201d","&hellip;":"\u2026","&eacute;":"\u00e9","&ouml;":"\u00f6"}
def unent(s):
    for k, v in ENT.items(): s = s.replace(k, v)
    return s

# ------------------------------------------------------------- references
# Assign numbers in order of first citation in the rendered body.
order = []
CITE = re.compile(r"\[(\d+)\]")
def _num(c): return int(c)

# We cite with explicit numbers, so validate the mapping is 1..25 and complete.
def build_reflist():
    keys = list(refs.REFS.keys())
    return keys

# The body cites numbers directly; keep the key order as the numbering order.
REFKEYS = list(refs.REFS.keys())
