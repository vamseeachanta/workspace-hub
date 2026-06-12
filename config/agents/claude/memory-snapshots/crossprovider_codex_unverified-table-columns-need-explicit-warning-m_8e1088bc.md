---
name: crossprovider codex unverified-table-columns-need-explicit-warning-m
description: Unverified table columns need explicit warning marking
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [data-quality, pdf-parsing, table-extraction]
---

When a PDF table cannot be parsed cleanly into aligned columns, emit one `raw_layout` column containing the unparsed text AND a header note 'columns unverified — needs manual/vision cleanup' rather than presenting mis-aligned columns as structured data. This prevents silent downstream misuse.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
