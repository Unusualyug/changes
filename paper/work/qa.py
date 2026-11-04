import re, json, sys, os
import pymupdf
from docx import Document
import build_common as BC

PDF = os.path.join(BC.OUTDIR, BC.OUTBASE + ".pdf")
DOCX = os.path.join(BC.OUTDIR, BC.OUTBASE + ".docx")

pdf = pymupdf.open(PDF)
pdftext = "\n".join(p.get_text() for p in pdf)
doc = Document(DOCX)
dtext = "\n".join(p.text for p in doc.paragraphs)
for t in doc.tables:
    for row in t.rows:
        dtext += "\n" + " | ".join(c.text for c in row.cells)

BAD = ["TBD", "{tab:", "{fig:", "<b>", "</b>", "<i>", "&nbsp;", "&mdash;", "&ndash;",
       "Not available before", "Lorem", "XXX", "[?]", "TODO"]
print("=== placeholder / markup scan ===")
for name, txt in (("PDF", pdftext), ("DOCX", dtext)):
    hits = [b for b in BAD if b in txt]
    print(f"{name}: {'CLEAN' if not hits else 'FOUND ' + str(hits)}")

print("\n=== citations ===")
nums = set(int(x) for x in re.findall(r"\[(\d+)\]", pdftext))
print("cited in PDF:", sorted(nums))
print("max:", max(nums), " missing from 1..25:", sorted(set(range(1, 26)) - nums))
refs_sec = pdftext[pdftext.index("REFERENCES"):]
refnums = set(int(x) for x in re.findall(r"^\[(\d+)\]", refs_sec, flags=re.M))
print("bibliography entries:", len(refnums), "uncited entries:", sorted(refnums - nums))
print("cited but absent from bibliography:", sorted(nums - refnums))

print("\n=== floats ===")
print("figures:", re.findall(r"Fig\. (\d)\.", pdftext)[:10])
print("tables:", re.findall(r"TABLE ([IVX]+)", pdftext))
print("pages:", pdf.page_count, "| docx tables:", len(doc.tables),
      "| docx inline images:", len(doc.inline_shapes))

print("\n=== numbers appearing in the PDF that must match the artifacts ===")
res = json.load(open("results.json"))
checks = {
 "macro AUC 0.771": "0.771", "Normal AUC 0.724": "0.724", "Pneumonia AUC 0.709": "0.709",
 "Cardiomegaly 0.805": "0.805", "Effusion 0.844": "0.844", "macro sens 0.638": "0.638",
 "macro spec 0.705": "0.705", "macro prec 0.323": "0.323", "macro F1 0.349": "0.349",
 "micro F1 0.407": "0.407", "n = 830": "830", "train 3,447": "3,447", "val 722": "722",
 "positives 643": "643", "epochs 8": "0.1485",
}
for k, v in checks.items():
    print(f"  {'ok ' if v in pdftext else 'MISS'} {k}")
print("\n=== stray artefacts ===")
for pat in [r"Section \w+, Table", r"Fig\.&nbsp;", r"\bTable \w+ and Fig", r"\?\?"]:
    m = re.findall(pat, pdftext)
    if m: print("  found:", pat, m[:4])
print("done")
