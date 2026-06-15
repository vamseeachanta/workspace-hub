---
name: crossprovider codex mechanical-extraction-parse-status-defaults-to-p
description: Mechanical extraction parse_status defaults to provisional-unverified
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [extraction, tables, verification]
---

Tables extracted via pdfplumber should be marked `parse_status: provisional-unverified` (never 'verified') because mechanical extraction is faithful to layout but not semantically correct (merged cells, OCR errors, etc.). These go to vision queue for verification.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
