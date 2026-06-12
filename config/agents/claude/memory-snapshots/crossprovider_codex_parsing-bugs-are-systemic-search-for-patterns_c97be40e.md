---
name: crossprovider codex parsing-bugs-are-systemic-search-for-patterns
description: Parsing bugs are systemic; search for patterns
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [llm-wiki, table-parsing, defect-hunting]
---

A single table-parsing defect (e.g. collapsed multi-row cells like '30 10 60' into one row) recurs across many tables in the same source/edition. Fix the named example, then grep the entire dataset for the pattern to catch all instances; single-instance fixes leave the systemic bug in place.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
