---
name: crossprovider codex ast-dependency-scanning-misses-string-selected-b
description: AST dependency scanning misses string-selected backends and dynamic imports
metadata:
  type: reference
  source: codex
  bridged: 2026-07-30
  tags: [dependency-analysis, ast-scanning, string-selection, missed-detection]
---

Static import scanning sees `import pandas` but not `pd.ExcelWriter(engine='xlsxwriter')`, `pd.read_hdf()` (requires PyTables), or `xr.open_dataset(engine='h5netcdf')`. Manual DYNAMIC_RUNTIME lists must be maintained separately; AST gives false assurance of completeness. This codebase broke once on uncaught string-selected engines.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
