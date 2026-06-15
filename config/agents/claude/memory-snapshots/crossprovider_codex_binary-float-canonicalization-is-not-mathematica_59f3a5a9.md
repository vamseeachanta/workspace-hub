---
name: crossprovider codex binary-float-canonicalization-is-not-mathematica
description: Binary float canonicalization is not mathematically exact
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [numeric-precision, float-representation, scoring-semantics]
---

Using `repr(float(...))` as an "exact" numeric tier is fundamentally limited: distinct high-precision values can collapse in binary representation (e.g., `9007199254740992` and `9007199254740993` both map to `9007199254740992.0`). This is the same class of precision loss that the fix was trying to prevent. Reserve float canonicalization for tolerant tiers only.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
