---
name: crossprovider gemini safe-numeric-conversions-with-explicit-none-and-
description: Safe numeric conversions with explicit None and zero handling
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [numeric-safety, type-conversion, data-semantics]
---

Implement _safe_float and _safe_float_or_none helpers to convert DataFrame values while distinguishing None (missing data), 0 (actual zero), and NaN. Use consistent conversion in row-to-domain-object mappers. This prevents silent type errors and preserves data semantics.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
