---
name: crossprovider codex string-selected-dependencies-bypass-ast-scanners
description: String-selected dependencies bypass AST scanners
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [dependencies, static-analysis, testing, python]
---

Static dependency analysis cannot detect engines/backends loaded via string arguments: pd.ExcelWriter(engine='xlsxwriter'), xr.open_dataset(engine='h5netcdf'), pd.read_hdf() requiring PyTables. This creates a class of hidden undeclared dependencies that pass contract checks until runtime.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
