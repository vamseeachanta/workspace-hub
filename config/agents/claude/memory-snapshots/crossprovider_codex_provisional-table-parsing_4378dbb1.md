---
name: crossprovider codex provisional-table-parsing
description: Provisional table parsing
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-handling, tables, verification-queue]
---

Extract tables via pdfplumber with `parse_status: PROVISIONAL` (never `verified`). Append raw/parsed CSVs to `_verification-queue.csv` in the domain's datasets/ directory and link in page frontmatter.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
