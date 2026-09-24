---
name: crossprovider codex image-only-pdf-filter
description: Image-only PDF filter
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [content-quality, filtering, garbage-detection]
---

Before writing a page, check extractable text character count via pdftotext. Skip negligible/OCR-only scans to the vision queue instead of creating garbage pages; character count is the gate metric.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
