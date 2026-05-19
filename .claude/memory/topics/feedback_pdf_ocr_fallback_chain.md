> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-19
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_pdf_ocr_fallback_chain.md

---
name: pdf-ocr-fallback-chain
description: "When pdftotext and PyMuPDF both return empty text on a PDF, treat it as image-rendered and OCR via PyMuPDF render to PNG → tesseract; pattern recurs for vendor/recruiter JDs, scanned contracts, printed-then-scanned docs"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 3537e768-7e6b-42e4-9a13-a4b0e3f1d9aa
---

When `pdftotext` AND `PyMuPDF (fitz)` both return 0 chars for a PDF, it has no text layer. Use the OCR fallback: PyMuPDF `page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))` → save PNG → `tesseract <png> - -l eng --psm 6` → stitch per page. ~5 sec/page sequential.

**Why:** Two-tool failure isolates the cause to "no embedded text," not to a Poppler/PyMuPDF disagreement. Without confirming this, you can waste time on encoding flags, PDF version downgrades, or chasing decoders. Verified 2026-05-12 on Harbour Energy / Zama JDs from a recruiter (8 of 9 attachments were image-rendered; only the FPSO Ops JD had a native text layer).

**How to apply:** Probe both extractors first via a length check (`len(page.get_text()) == 0` for fitz; empty `.txt` file for pdftotext). On confirmed image-only, render at 300 DPI minimum (lower DPIs degrade tesseract accuracy significantly on JD-style mixed text/headings). Use `--psm 6` (uniform block of text) as the default; `--psm 4` (single column) for multi-column documents. Stitch with page-break markers so the output is greppable. Related: [[reference_kaggle_cli_kgat_auth]] for the same kind of "tool surprised me" tool-quirk genre.
