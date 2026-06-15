---
name: crossprovider codex unbounded-corpus-scans-need-windowing-or-cached-
description: Unbounded corpus scans need windowing or cached results
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [performance, scaling, optimization]
---

A deprioritization scan that opens all 17k CSVs in the corpus for every batch selection is prohibitively slow. Either use bounded overfetch (load top N, stop early if sufficient), cache detector results, or sample the corpus for interactive runs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
