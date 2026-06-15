---
name: crossprovider codex source-table-row-contracts-must-match-across-loc
description: Source table row contracts must match across local and centralized schemas
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [schema-consistency, testing, source-map]
---

Page-local source tables in wiki content must use the same row fields and format as the centralized source map. URL-membership tests alone will miss row-field drift (e.g., missing `intended_use`, `visible_version_or_date`, `accessed_date`). Require validation that parses every source row for required columns and non-empty fields.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
