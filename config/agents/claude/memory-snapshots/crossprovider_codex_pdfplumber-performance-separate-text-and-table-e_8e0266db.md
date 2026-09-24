---
name: crossprovider codex pdfplumber-performance-separate-text-and-table-e
description: pdfplumber Performance: Separate Text and Table Extraction
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [performance, pdf-extraction, pdfplumber]
---

pdfplumber.extract_tables() firing on every page is slow on large PDFs (400+ pages can dominate session time). Use pdftotext -layout for full text reading and caption discovery, pdfplumber only for explicit table extraction. Separates concerns and avoids the text-extraction bottleneck.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
