---
name: crossprovider codex in-place-updates-must-preserve-non-refresh-colum
description: In-place updates must preserve non-refresh columns by name
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [incremental-updates, column-preservation, data-integrity]
---

When refresh/rebuild touches a table, distinguish refresh-owned columns (e.g., size, mtime, status) from external columns (e.g., title, discipline, extraction_status, content_hash). Update only refresh-owned columns; preserve others by name to avoid clobbering external work. Use explicit column lists in UPDATEs, not wholesale replacements.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
