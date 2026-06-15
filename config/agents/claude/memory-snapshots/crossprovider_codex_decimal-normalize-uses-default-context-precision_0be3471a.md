---
name: crossprovider codex decimal-normalize-uses-default-context-precision
description: Decimal.normalize() uses default context precision of 28 digits
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [numeric-precision, python-stdlib, decimal-context]
---

When using Python's `decimal.Decimal(...).normalize()` for exact numeric canonicalization, values with >28 significant digits still collapse to the context precision even if they were created from exact strings. Widen the decimal context before normalizing, or accept that "exact tier" is bounded by 28 digits. This was a subtle precision-loss path in goldset validation scoring.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
