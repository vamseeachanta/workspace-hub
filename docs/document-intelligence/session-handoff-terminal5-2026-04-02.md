# Session Handoff — Terminal 5: Document Intelligence Pipeline Hardening
**Date:** 2026-04-02  
**Agent:** Claude/Hermes (overnight batch)  
**Prompt:** docs/plans/overnight-prompts/terminal-5-doc-intelligence.md

---

## Completed Tasks

### TASK 1: OCR Parser for Scanned PDFs (#1617) — CLOSED
- **Scripts:** scripts/document_intelligence/ocr_parser.py, scripts/document-intelligence/ocr-parser.py
- **Tests:** tests/document-intelligence/test_ocr_parser.py (9 tests, all pass)
- **Features:**
  - `is_scanned_pdf()` — detects image-only PDFs via pdfplumber text threshold
  - `ocr_extract()` — full OCR via pytesseract + pdf2image
  - `mixed_pdf_extract()` — hybrid text+OCR for mixed PDFs
  - Returns `DocumentManifest` (same schema as existing pipeline)
  - Graceful fallback when tesseract not installed (clear error message)
  - Handles corrupt/missing PDFs without exceptions
- **Note:** tesseract-ocr is NOT installed on dev-primary — see #1640

### TASK 2: XLSX Formula Extraction 50MB Limit (#1619) — CLOSED
- **Commit:** e3dfeaea
- **Scripts:** scripts/document_intelligence/xlsx_formula_extractor.py, scripts/document-intelligence/xlsx-formula-extractor.py
- **Tests:** tests/document-intelligence/test_xlsx_extractor.py (8 tests, all pass)
- **Changes:**
  - MAX_SIZE_MB raised from 15 to 50 (new extractor + existing run_poc_extraction.py)
  - Pass 1 uses openpyxl read_only=True for memory-efficient streaming
  - JSON output: {sheet, cell_ref, formula, cached_value} per formula
  - CLI: --input, --output flags

### TASK 3: Conference Index Plan (#1608) — OPEN (plan only)
- **Commit:** ce82407a
- **Plan:** docs/document-intelligence/conference-index-plan.md
- **Script:** scripts/document-intelligence/index-conferences.sh (stub with full batch loop)
- **Survey results:**
  - 30 collections, 38,526 files, 28 GB total
  - 57.1% PDF (21,996), 13.7% HTML (5,283), ~28% skip (images/binaries/index artifacts)
  - ~27,683 indexable files (71.9%)
  - 4-phase priority ordering, est. 9-17 hours
  - Stub script: --phase, --collection, --batch-size, --dry-run, checkpointing

---

## New GitHub Issues Created

| # | Title | Priority | Dependencies |
|---|-------|----------|-------------|
| #1640 | Install tesseract-ocr and validate OCR parser on real scanned PDFs | Medium | #1617 (closed) |
| #1641 | Execute conference indexing Phase 1 — 1,032 files | High | #1608, #1640 |
| #1642 | Execute conference indexing Phases 2-4 — 37,494 files | Medium | #1641 |
| #1643 | Register OCR parser in doc-intelligence parser registry | Medium | #1617, #1640 |
| #1644 | Stress-test XLSX formula extractor with real 15-50MB files | Low | #1619 (closed) |

## Issues Closed
- #1617 — OCR parser implemented
- #1619 — XLSX 50MB limit with streaming

---

## File Manifest (all new/modified files)

```
scripts/document_intelligence/__init__.py           (new — empty)
scripts/document_intelligence/ocr_parser.py         (new — 340 lines)
scripts/document_intelligence/xlsx_formula_extractor.py (new — 230 lines)
scripts/document-intelligence/__init__.py           (new — empty)
scripts/document-intelligence/ocr-parser.py         (new — copy of above)
scripts/document-intelligence/xlsx-formula-extractor.py (new — copy of above)
scripts/document-intelligence/index-conferences.sh  (new — 208 lines, stub)
tests/document-intelligence/__init__.py             (new — empty)
tests/document-intelligence/test_ocr_parser.py      (new — 9 tests)
tests/document-intelligence/test_xlsx_extractor.py  (new — 8 tests)
docs/document-intelligence/conference-index-plan.md (new — plan)
scripts/data/doc_intelligence/run_poc_extraction.py (modified — MAX_SIZE_MB 15→50)
```

## Next Steps (priority order)
1. Install tesseract-ocr on dev-primary (#1640) — unblocks OCR pipeline
2. Run conference Phase 1 (#1641) — quick validation of batch indexing
3. Register OCR in parser registry (#1643) — makes OCR transparent
4. Run conference Phases 2-4 (#1642) — full 38K file indexing
5. Stress-test XLSX extractor (#1644) — validate real-world performance
