---
name: crossprovider codex image-only-and-near-empty-pdfs-skip-vision-queue
description: Image-only and near-empty PDFs → skip + vision queue
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [content-filtering, image-only, quality-gate]
---

PDFs with zero extractable text (scans, screenshots, image-only renders) do not become wiki pages. Add to a skip manifest and enqueue for future OCR/manual review instead. Never create garbage pages with negligible text to avoid bloating the corpus with low-signal content.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
