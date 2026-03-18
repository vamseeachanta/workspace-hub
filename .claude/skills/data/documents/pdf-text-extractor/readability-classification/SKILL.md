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

### Final Corpus State (WRK-1277, 2026-03-17)

| Classification | Count | Percentage |
|---------------|-------|-----------|
| native | 623,455 | 60.3% |
| machine | 278,899 | 27.0% |
| ocr-needed | 92,042 | 8.9% |
| missing | 27,476 | 2.7% |
| error | 6,221 | 0.6% |
| mixed | 5,246 | 0.5% |
| **Total classified** | **1,033,933** | **96.7%** |

Error reduction: 296,626 → 6,221 (97.9% recovery). Remaining errors are genuine
edge cases (corrupt PDFs, missing files, extremely complex documents).

### Classification Method

**Use pdftotext (poppler) for batch classification** — not pdfplumber:

```bash
# Classify all PDFs with parallel workers (resume-safe)
uv run --no-project python scripts/data/document-index/enrich-readability.py \
    --workers 10 --resume
```

Use `--workers 10` for bulk enrichment to parallelize across CPU cores. The `--resume`
flag skips already-classified entries, making it safe to restart after interruption.

> **WARNING (WRK-1277)**: The original `enrich-readability.py` used pdfplumber in
> `ProcessPoolExecutor` — this hung in D-state on NTFS/NFS mounts. The proven pattern
> is pdftotext via `subprocess.run(timeout=30)` with 8 workers (see
> `pdf/pdftotext-poppler` sub-skill for code). Throughput: ~49 files/sec vs ~1.3 with
> pdfplumber.
