# Scanned PDF — OCR fallback chain

For image-only PDFs (scanned documents) and image files (PNG / JPG)
that carry text. Codifies the existing
`feedback_pdf_ocr_fallback_chain` rule.

## When to route here

The PDF protocol routes here when `pdftotext` AND `PyMuPDF.get_text()`
both return 0 chars on pages that visibly contain text.

Signals:
```bash
pdftotext <source.pdf> - | wc -c    # near-zero output
pdffonts <source.pdf>                # no embedded fonts
```

## Pre-extraction estimate

For scanned PDFs:

| Page-image quality | Estimate |
|---|---|
| 300 DPI, clean scan, standard font | 0.90 |
| 200 DPI or below | 0.70 |
| Rotated / skewed pages | 0.60 (need pre-rotation) |
| Faxed / heavily degraded | 0.40 |
| Handwritten | 0.10 (tesseract is poor at handwriting; consider manual transcription) |

For images:

| Source | Estimate |
|---|---|
| Screenshot of clean text | 0.95 |
| Photo of printed document | 0.80 |
| Photo with shadows / perspective | 0.60 |
| Whiteboard / handwriting | 0.20 |

## Extraction: `tesseract` via PyMuPDF render

```python
import fitz
import subprocess
import tempfile
from pathlib import Path

doc = fitz.open("<source.pdf>")
extracted = []
for page_num, page in enumerate(doc):
    # Render at 300 DPI
    pix = page.get_pixmap(dpi=300)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        pix.save(tmp.name)
        # OCR
        result = subprocess.run(
            ["tesseract", tmp.name, "-", "--psm", "6", "-l", "eng"],
            capture_output=True, text=True
        )
        extracted.append((page_num, result.stdout))
```

`--psm 6` = "Assume a single uniform block of text". Other PSM modes:
- `--psm 3` = automatic page segmentation (default, but slower)
- `--psm 11` = sparse text (useful for forms / labels)
- `--psm 12` = sparse text with OSD (orientation + script detection)

For images directly:
```bash
tesseract <source.png> <output> --psm 6 -l eng
```

## Layout-preserving OCR

For multi-column scanned papers, single-column `--psm 6` interleaves
columns. Use:

```bash
tesseract <source.png> <output> --psm 3 -c preserve_interword_spaces=1
```

Or pre-segment columns with `pdf2image` + `opencv` before OCR.

## Post-extraction yield

Two-pass measurement:

1. **Coverage**: how many pages produced ≥ 200 chars of OCR output?
2. **Quality spot-check**: on 5 random pages, manually compare 100-char
   samples against the source image. Estimate per-character accuracy.

```python
total_pages = len(doc)
recovered = sum(1 for _, text in extracted if len(text.strip()) > 200)
coverage = recovered / total_pages

# Quality estimate is human-in-the-loop — record in extraction_yield_lost
```

Combined yield: `coverage × quality_estimate`, capped at 0.95
(OCR is never perfect; reserve ≥ 0.05 for known errors).

## Anchor format

`[[sources/<slug>]]:p<page>:OCR`

The `:OCR` suffix is the trust signal — readers/reviewers know to
verify against the source image for any cited value. Compare to
`:p<page>:¶<paragraph>` for text-extracted PDFs, where trust is high.

## Spot-check protocol

For every standards page or methodology page that cites OCR'd content:

1. Open the source PDF at the cited page
2. Locate the cited passage visually
3. Verify the wiki claim matches the source within OCR tolerance
4. If mismatch: file an audit per `research/llm-wiki-audit-feedback-loop`
   with the actual source text, route to revise

## Common pitfalls

- **Skewed scans**: OCR accuracy drops 30%+ on >2° skew; pre-rotate with
  `deskew` or `opencv.minAreaRect` before tesseract
- **Marginalia / page numbers**: OCR includes them as text; strip in
  post-processing
- **Footnotes interleaved with body**: tesseract is page-flat; use
  layout analysis (`tesseract --tessdata-dir <dir> --psm 1`) to
  segment
- **Multi-language documents**: pass `-l eng+deu` etc. but accuracy drops
- **Equations / formulas**: tesseract is poor; transcribe to KaTeX
  manually; flag in `extraction_yield_lost`
- **Tables**: OCR flattens; use `tabula-java` or `camelot` (which itself
  requires text-based PDF) or manual transcription
- **Stamps / handwriting / annotations**: tesseract treats them as noise;
  flag in `extraction_yield_lost` if material

## Quality upgrade chain

If yield is < 0.80 and the source is critical:

1. **Re-scan at higher DPI** if the source is physical
2. **Deskew + denoise** with `opencv` or `imagemagick -despeckle`
3. **Train a tesseract model** on the document's font (advanced)
4. **Manual transcription** for the lost passages, flagged in the
   summary page

Record every upgrade attempt in `extraction_yield_lost` with date and
new yield.
