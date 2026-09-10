---
name: crossprovider codex string-selected-dependencies-bypass-static-ast-a
description: String-selected dependencies bypass static AST analysis
metadata:
  type: reference
  source: codex
  bridged: 2026-07-30
  tags: [dependency-scanning, python-ast, testing-coverage]
---

Dependency scanning tools using AST analysis miss dynamic backend selections via string parameters like engine='h5netcdf' or pd.read_hdf(). These produce ModuleNotFoundError on clean installations despite passing static checks. Maintain a manual list of known string-selected deps alongside automated scanning.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
