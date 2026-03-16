---
name: pdf-text-extractor-readability-classification
description: 'Sub-skill of pdf-text-extractor: Readability Classification.'
version: 1.2.0
category: data
type: reference
scripts_exempt: true
---

# Readability Classification

## Readability Classification


Before extracting text from a large PDF collection, classify each PDF's readability
using `enrich-readability.py`. This determines which extraction strategy to use:

| Classification | Meaning | Extraction strategy |
|---------------|---------|-------------------|
| `machine` | Text layer present, directly extractable | pdfplumber / PyMuPDF |
| `ocr-needed` | Scanned image, no text layer | tesseract / doctr / azure-doc-intelligence |
| `mixed` | Some pages machine-readable, some scanned | Hybrid — extract text pages, OCR image pages |
| `error` | Corrupted or unreadable | Skip; log for manual review |

**Key finding**: 27-30% of project PDFs are scanned with no text layer. Attempting
direct text extraction on these returns empty strings — always classify first.

```bash
# Classify all PDFs with parallel workers (resume-safe)
uv run --no-project python scripts/data/document-index/enrich-readability.py \
    --workers 10 --resume
```

Use `--workers 10` for bulk enrichment to parallelize across CPU cores. The `--resume`
flag skips already-classified entries, making it safe to restart after interruption.
