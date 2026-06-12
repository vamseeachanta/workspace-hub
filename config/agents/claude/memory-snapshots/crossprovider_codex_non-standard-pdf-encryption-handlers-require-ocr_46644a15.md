---
name: crossprovider codex non-standard-pdf-encryption-handlers-require-ocr
description: Non-standard PDF encryption handlers require OCR fallback for metadata
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [pdf-ingest, encryption, ocr, tooling]
---

Security handlers like FOPN_foweb block pdftotext and pdfinfo entirely. Workaround: extract pages as temp images, apply OCR locally, delete temp files. Use for metadata/title inference when embedded text fails.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
