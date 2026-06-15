---
name: crossprovider codex image-only-pdf-detection-pdftotext-pdffonts-pdfi
description: Image-only PDF detection: pdftotext, pdffonts, pdfimages signals
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [pdf, image-only, classification, ocr]
---

`pdftotext` returns only form-feeds, `pdffonts` lists no fonts, `pdfimages` shows CCITT scans = image-only. Use local `tesseract` on temporary renders only (no file writes) for OCR; never extract or commit raw scans to the repo.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
