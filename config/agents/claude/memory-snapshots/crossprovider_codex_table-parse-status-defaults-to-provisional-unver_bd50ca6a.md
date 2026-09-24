---
name: crossprovider codex table-parse-status-defaults-to-provisional-unver
description: Table parse_status defaults to provisional-unverified, never verified
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ingest, tables, parse-status, default]
---

When extracting tables from source PDFs, mark them `provisional-unverified parsed` (if parsed by tool) or `raw-unverified` (if manually transcribed). The default is NEVER `verified`. This signals that human or tool validation is pending and prevents false confidence in derived data.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
