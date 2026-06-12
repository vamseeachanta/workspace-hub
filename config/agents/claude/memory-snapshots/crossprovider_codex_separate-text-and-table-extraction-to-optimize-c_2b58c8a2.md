---
name: crossprovider codex separate-text-and-table-extraction-to-optimize-c
description: Separate text and table extraction to optimize cost
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [pdf-extraction, performance-optimization, tooling-pattern]
---

Use pdftotext -layout for full-document text extraction and caption discovery; use pdfplumber only for table extraction. Text extraction can be slow on large PDFs (MIL-217 material tables, hydrostatics refs); separating concerns keeps the ingest inside session bounds.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
