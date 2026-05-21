# PDF extraction — coverage protocol

Reference for the SKILL.md routing table. Covers text-based PDFs.
Scanned/image PDFs route to `scanned-pdf-ocr-fallback.md`.

## Pre-extraction estimate

```bash
# Structural inspection
pdfinfo <source.pdf>                        # total pages, encrypted, version
pdffonts <source.pdf> | head                # font embedding → text vs scanned
qpdf --check <source.pdf> 2>&1 | head -20   # damage / page-tree health

# Quick yield estimate:
total_pages=$(pdfinfo <source.pdf> | awk '/^Pages:/ {print $2}')
text_pages=$(pdftotext -nopgbrk <source.pdf> - 2>/dev/null | grep -c $'\f')
estimate=$(echo "scale=2; $text_pages / $total_pages" | bc)
echo "extraction_estimate: $estimate"
```

Set `extraction_estimate` based on:

| Indicator | Estimate baseline |
|---|---|
| All pages have embedded fonts, `pdftotext` recovers text on all pages | 0.95 |
| Mixed text + image pages | (text_pages / total_pages); typically 0.5–0.85 |
| No embedded fonts, all images | 0.0 baseline (OCR can lift to 0.8–0.95) → route to `scanned-pdf-ocr-fallback.md` |
| Encrypted | 0.0 → defer until decrypted |
| Damaged page tree | 0.0 → defer; flag for source replacement |

## Primary extractor: `pdftotext -layout`

```bash
pdftotext -layout -nopgbrk <source.pdf> <output.txt>
```

`-layout` preserves columns; `-nopgbrk` removes form-feed delimiters
(use page boundary detection in post-processing instead).

## Fallback: PyMuPDF (`fitz`)

When `pdftotext` returns 0 chars on a specific page that should be text:

```python
import fitz
doc = fitz.open("<source.pdf>")
for page_num, page in enumerate(doc):
    text = page.get_text()
    if not text.strip():
        # try the alternate text extractor
        text = page.get_text("rawdict")  # structured extraction
```

Per `feedback_pdf_ocr_fallback_chain`: pdftotext + PyMuPDF both returning
0 chars on a page is the signal to route that page to OCR.

## Post-extraction yield measurement

```bash
# Recovered pages = pages with > N chars of extracted text
threshold=200
recovered_pages=$(awk 'BEGIN{count=0} /^\f/{if(curr>'$threshold')count++; curr=0; next} {curr+=length($0)} END{print count}' <output.txt>)
yield=$(echo "scale=2; $recovered_pages / $total_pages" | bc)
echo "extraction_yield: $yield"
```

## Anchor format for cites

`[[sources/<slug>]]:p<page>:¶<paragraph-index>`

Paragraph index is 1-based within the page after `pdftotext -layout`
post-processing splits on blank lines.

## Spot-check

Open the source PDF in a viewer. Verify the extracted text matches the
visible content on 5–10 random pages. Flag mismatches in
`extraction_yield_lost`.

## Common pitfalls

- Two-column layouts: `-layout` mostly handles, but verify
- Mathematical content: equations render as character salad; transcribe
  to KaTeX manually for any equation cited in wiki content
- Tables: `pdftotext` flattens; use `tabula-py` or `camelot` for
  structured table extraction when needed
- Footnotes interleave with body text in layout mode; verify
- Headers/footers repeat on every page; strip in post-processing
