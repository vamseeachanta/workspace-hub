---
name: crossprovider hermes pdf-rendering-fallback-convert-to-images
description: PDF rendering fallback: convert to images
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [document-handling, pdf-processing, workarounds]
---

PDFs that fail to render cleanly in browser (scanned documents, complex layouts) can be converted to PNG images using `pdftoppm -f <page> -l <page> -png`. Allows visual inspection and reference when text extraction or browser rendering fails.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
