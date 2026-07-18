---
name: crossprovider codex negative-residual-interval-arithmetic-requires-i
description: Negative residual interval arithmetic requires inverted bounds
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [arithmetic, correctness, finance]
---

When computing percentage residuals for range-bounded totals, the formula [Rlo/Thi, Rhi/Tlo] is valid only for nonnegative residuals. For negative residuals (shortfalls), the bounds invert and can be much wider; failing to account for this understates overruns.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
