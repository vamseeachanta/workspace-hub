# DOCX extraction — coverage protocol

## Pre-extraction estimate

```bash
unzip -l <source.docx> | head -30
```

Inspect:
- `word/document.xml` — body text
- `word/embeddings/` — embedded Excel/PDF that may carry critical data
- `word/media/` — images (may need OCR if they carry text)
- `customXml/`, `word/footnotes.xml`, `word/endnotes.xml` — supplementary text

`extraction_estimate` baseline:

| Indicator | Estimate |
|---|---|
| Document body + standard footnotes only | 0.95 |
| Embedded Excel objects with data not in body | 0.70 (embeddings need separate extraction) |
| Image-only content (screenshots of tables, equations as images) | 0.50 (needs OCR on media) |
| Password-protected | 0.0 |

## Primary extractor: `python-docx`

```python
from docx import Document
doc = Document("<source.docx>")
for i, para in enumerate(doc.paragraphs):
    if para.text.strip():
        print(f"¶{i}: {para.text}")
for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            print(cell.text)
```

Limitations:
- Embedded Excel objects: `python-docx` does NOT recurse into them; use
  `zipfile` + `openpyxl` directly on `word/embeddings/oleObject1.xlsx`
- Equations: rendered as `<m:oMath>` elements; `python-docx` skips them;
  use `python-docx-oss` or post-process the raw XML
- Track-changes / comments: not extracted by default; use `python-docx`'s
  comments API if reviewing redlined documents

## Fallback: `pandoc`

```bash
pandoc -f docx -t markdown <source.docx> -o <output.md>
```

Pandoc handles equations (LaTeX-ish output), comments (visible), and
preserves heading structure. Use when `python-docx` misses content.

## Post-extraction yield

```python
import docx
doc = docx.Document("<source.docx>")
total_paragraphs = len(doc.paragraphs)
extracted_paragraphs = sum(1 for p in doc.paragraphs if p.text.strip())
yield_ = extracted_paragraphs / total_paragraphs
```

Add embedded-object recovery to the count if you extracted from `word/embeddings/`.

## Anchor format

`[[sources/<slug>]]:¶<paragraph-id>`

Paragraph ID is the index in `doc.paragraphs` (0-based). Stable across
re-extractions of the same document.

For embedded Excel: `[[sources/<slug>]]:¶<id>:embedded-<sheet>!<cell>`

## Spot-check

Open the source DOCX in Word/LibreOffice. Verify extracted text matches
on 5–10 random paragraphs. Verify any embedded objects are accounted for
in `extraction_yield_lost` if not recovered.

## Common pitfalls

- Headers/footers: `python-docx` does not include them in `doc.paragraphs`; use `doc.sections[i].header.paragraphs`
- Comments and tracked changes: not in default extraction
- Cross-reference fields (`{REF _Ref...}`) render as raw codes — resolve via the field's cached text
- Equation Editor objects (legacy): not extracted by `python-docx`; OCR the rendered equation image
- Embedded fonts in body run as styling; ensure encoding survives extraction
