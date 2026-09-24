---
name: crossprovider codex image-only-detection-pdfimages-list-near-zero-pd
description: Image-only detection: pdfimages list + near-zero pdftotext output → skip and vision queue
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [image-only, skip-criteria, pdf-detection, safety-gate]
---

Combine `pdfimages -list` output (detects CCITT page images) with pdftotext character count (~0). Image-only PDFs go to _skipped.csv + #135 vision queue; do NOT create empty/garbage-title pages. Examples: single-page wire-transfer form, API RP 520 Part II scan, API RP 16Q riser PDF.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
