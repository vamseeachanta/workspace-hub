---
name: crossprovider codex numeric-cell-density-ranks-data-table-candidates
description: Numeric-cell density ranks data-table candidates better than file order
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [table-classification, vision-batching, heuristic-ordering]
---

When vision-reviewing flagged rows, select by numeric-data-cell count (cells with digits in non-header rows) rather than alphabetical order. Front-matter (ISBN/ICS/copyright pages) scores 0 cells; real tables score 102–166+. Use n×3 over-fetch and sort by density to surface genuine tables early in batches.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
