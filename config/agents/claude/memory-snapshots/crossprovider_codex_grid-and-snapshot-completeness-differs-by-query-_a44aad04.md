---
name: crossprovider codex grid-and-snapshot-completeness-differs-by-query-
description: Grid and snapshot completeness differs by query strategy; targeted queries beat state filters
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [queries, completeness, state-filtering, snapshot-design]
---

Querying by state (`--state open`) omits closed items but returns complete results for the selected state. When you need completeness across states (e.g., closed issues with labels), target the specific records by their known identifiers instead of filtering. Open-only snapshots are incomplete for closed items and can silently report false negatives.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
