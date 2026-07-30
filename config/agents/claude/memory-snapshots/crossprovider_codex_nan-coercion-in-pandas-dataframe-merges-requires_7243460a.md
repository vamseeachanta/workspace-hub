---
name: crossprovider codex nan-coercion-in-pandas-dataframe-merges-requires
description: NaN coercion in pandas DataFrame merges requires explicit handling
metadata:
  type: reference
  source: codex
  bridged: 2026-07-06
  tags: [data-handling, json-serialization, pandas]
---

When merging DataFrames with partial columns (e.g., oil-only vs gas-only rows), pandas `NA`/`NaN` values do not coerce with Python's `or 0.0` idiom. Use explicit `pd.isna()` checks or `.fillna()` before JSON serialization, and enforce `json.dumps(..., allow_nan=False)` to prevent standards-noncompliant output (bare `NaN` literals break `JSON.parse` in browsers).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
