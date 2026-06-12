---
name: crossprovider codex pdfplumber-targeted-page-geometry-pass-avoids-bo
description: pdfplumber targeted page-geometry pass avoids bottleneck
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [pdf-processing, performance-optimization, batch-processing]
---

For large PDFs (e.g., N-004 with 500+ pages), applying page-geometry detection to every page is slow. Instead: use text extraction to identify candidate table pages first, then apply expensive `pdfplumber` geometry parsing only to those pages. Reduces N-004 processing from hours to minutes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
