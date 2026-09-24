---
name: crossprovider codex cached-excel-values-are-not-reliable-test-oracle
description: Cached Excel values are not reliable test oracles without freshness checks
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, excel, fixtures]
---

XLSX cached formula results can be missing or stale if the workbook wasn't recalculated before save. When using cached values for test assertions, validate cache presence and freshness first. Synthetic openpyxl fixtures typically have no cached results, so use precomputed Excel files or hand-crafted XML for cache-dependent tests.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
