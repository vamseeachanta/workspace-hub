---
name: crossprovider codex success-metrics-need-explicit-denominator-rules
description: Success metrics need explicit denominator rules
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [acceptance-criteria, metrics, batch-validation]
---

"90% classified" is ambiguous: 90% of total docs, attempted docs, or non-duplicates? Define denominator in acceptance criteria: what counts as classified vs skipped vs errored. Resume-safe skip tracking (SHA-based) affects denominator interpretation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
