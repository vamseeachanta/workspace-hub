---
name: crossprovider codex cached-excel-values-unreliable-for-test-oracles-
description: Cached Excel values unreliable for test oracles in formula extraction
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [xlsx-extraction, test-fixtures, ground-truth]
---

Workbooks may have missing or stale cached values if not recalculated before save, making cached-result-as-ground-truth TDD infeasible. For formula extraction, classify cells as cached_ok, cached_missing, cached_suspect instead of blindly asserting cached values; only emit pytest assertions for cached_ok cells.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
