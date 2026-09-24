---
name: crossprovider codex ast-based-dependency-detection-misses-string-sel
description: AST-based dependency detection misses string-selected backends
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [dependencies, static-analysis, python]
---

Static import analysis cannot catch dynamic backend selection like engine='xlsxwriter' or pd.ExcelWriter(engine='...'). Undeclared dependencies hidden in string arguments pass AST scans but fail on clean installations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
