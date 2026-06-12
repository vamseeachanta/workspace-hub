---
name: crossprovider codex pandas-type-coercion-must-use-errors-coerce-for-
description: Pandas type coercion must use errors='coerce' for robustness
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [pandas, data-pipeline, type-safety]
---

Multiple crashes from `int(df[col])` and `df[col].str.strip()` on non-standard types (sessions 9, 17, 18). Use `pd.to_numeric(..., errors='coerce')` or `.astype(..., errors='coerce')` instead; validate column existence before access.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
