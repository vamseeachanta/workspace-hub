---
name: crossprovider codex csv-extraction-from-pdf-conversion-produces-pred
description: CSV extraction from PDF conversion produces predictable symbol artifacts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-extraction, csv, pdf-processing, quality-assurance]
---

Degree symbols become control characters, subscripts are malformed, and record terminators (CRLF vs LF) can drift. When correcting extracted CSVs, preserve byte-shape and record-terminator consistency by spot-checking against visual sources (PDFs) rather than assuming extraction is clean.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
