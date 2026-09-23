---
name: crossprovider codex overlaps-require-union-not-sum-for-rollup-across
description: Overlaps require union, not sum, for rollup across boundaries
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [correctness, intervals, rollup]
---

Summing per-rig days double-counts overlapping weeks (especially at sidetrack transitions where one WAR week codes to two bores). API12→API10 rollup must union intervals, not sum daily totals.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
