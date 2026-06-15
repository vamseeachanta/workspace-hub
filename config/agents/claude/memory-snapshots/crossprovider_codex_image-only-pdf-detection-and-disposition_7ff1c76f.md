---
name: crossprovider codex image-only-pdf-detection-and-disposition
description: Image-only PDF detection and disposition
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [pdf-screening, image-only-handling, quality-control]
---

PDFs with negligible extracted text (pdftotext returns <100 chars or only form feeds) detected via character-count probe and pdfimages inspection. Disposition: add to _skipped.csv with reason, queue for vision/OCR processing (#135 queue), never convert to near-empty wiki pages. Preserves archive quality and defers costly OCR to a separate verification lane.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
