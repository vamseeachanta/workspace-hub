---
name: crossprovider codex distinguish-image-only-pdfs-from-born-digital-us
description: Distinguish image-only PDFs from born-digital using pdffonts and pdfimages
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pdf-processing, automation, content-analysis]
---

`pdftotext` alone returns only form-feeds for image-only scans. Use `pdffonts` (no output = no embedded fonts) and `pdfimages` (one per page with CCITT compression = likely scan) to diagnose whether a PDF is born-digital or image-only before deciding to skip, OCR, or ingest.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
