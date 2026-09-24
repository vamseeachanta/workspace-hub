---
name: crossprovider codex pandas-aggregation-on-mixed-type-columns-fails-s
description: Pandas aggregation on mixed-type columns fails silently or produces incorrect results
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-handling, pandas, type-safety]
---

Data analysis modules showed failures: `min()/max()` on NaN, `.sum()` on object columns, and `.strip()` on mixed-type columns converting non-strings to NaN. Always validate dtype before aggregation; use explicit coercion or error on type mismatches.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
