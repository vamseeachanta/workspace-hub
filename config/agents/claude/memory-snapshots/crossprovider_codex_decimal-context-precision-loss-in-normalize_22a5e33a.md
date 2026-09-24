---
name: crossprovider codex decimal-context-precision-loss-in-normalize
description: Decimal context precision loss in normalize()
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [numeric-normalization, decimal-precision, python]
---

When using Python's `Decimal.normalize()`, it respects the default decimal context precision (28 significant digits), causing precision collapse for values exceeding this threshold. Widening the context with `localcontext(Context(prec=...))` before normalize() is necessary for exact-tier numeric canonicalization.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
