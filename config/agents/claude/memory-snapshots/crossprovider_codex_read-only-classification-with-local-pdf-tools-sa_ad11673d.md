---
name: crossprovider codex read-only-classification-with-local-pdf-tools-sa
description: Read-only classification with local PDF tools: safe discovery phase
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [pdf, tools, classification, read-only]
---

Use `pdfinfo` (metadata), `pdftotext` (char extraction), `pdffonts` (font inventory), `pdfimages` (scan detection), and optional `tesseract` (OCR on temp renders). No file writes, no repo commits; safe for pure-discovery phases where you only report classifications.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
