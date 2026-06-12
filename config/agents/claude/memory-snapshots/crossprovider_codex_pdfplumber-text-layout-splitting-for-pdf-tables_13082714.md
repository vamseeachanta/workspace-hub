---
name: crossprovider codex pdfplumber-text-layout-splitting-for-pdf-tables
description: pdfplumber > text-layout splitting for PDF tables
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [pdf-processing, table-extraction, tool-choice]
---

Prior attempts using `pdftotext -layout` line-splits produce mis-aligned columns and appear structured but are wrong. Using `pdfplumber` with a targeted two-pass approach (text extraction to identify table pages, then real table parsing on those pages only) produces clean CSVs and avoids expensive geometry detection on large PDFs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
