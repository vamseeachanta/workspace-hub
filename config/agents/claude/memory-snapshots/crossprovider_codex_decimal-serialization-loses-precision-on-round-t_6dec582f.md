---
name: crossprovider codex decimal-serialization-loses-precision-on-round-t
description: Decimal serialization loses precision on round-trip
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [serialization, numeric-types, precision]
---

Decimal.to_string() on integral Decimals (e.g., `Decimal("100")` → `"1"`) strips trailing zeros. Re-parsing truncated strings corrupts numeric values and can silently change sort order or comparisons. Serialize using fixed-precision formats (e.g., `Decimal.to_eng_string()`) or store raw string representation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
