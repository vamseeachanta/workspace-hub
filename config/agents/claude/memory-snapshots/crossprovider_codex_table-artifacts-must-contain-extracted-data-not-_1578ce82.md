---
name: crossprovider codex table-artifacts-must-contain-extracted-data-not-
description: Table artifacts must contain extracted data, not caption inventories
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [structured-data, extraction, artifacts]
---

CSV/table artifacts for document ingest must emit actual extracted data (column headers, rows, cell values), not caption counts or inventory lists. Prose-embedded tables without separate extraction represent information loss. Tests must verify table extraction is implemented, not mocked.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
