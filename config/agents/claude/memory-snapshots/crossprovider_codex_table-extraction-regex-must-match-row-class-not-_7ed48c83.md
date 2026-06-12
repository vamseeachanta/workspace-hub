---
name: crossprovider codex table-extraction-regex-must-match-row-class-not-
description: Table extraction regex must match row class not column count
metadata:
  type: reference
  source: codex
  bridged: 2026-05-27
  tags: [table-extraction, data-loss, regex]
---

Mixed-column sub-tables within the same section cause row loss when extraction assumes fixed column count. Safe: use row-class pattern like `| [` to select rows independent of column structure.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
