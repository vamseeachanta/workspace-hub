---
name: crossprovider gemini bash-regex-parsing-of-tool-output-is-brittle
description: Bash regex parsing of tool output is brittle
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [bash-scripting, testing, tool-integration, brittleness]
---

Parsing pytest/ruff/mypy output with bash regex (WRK-1054, 1056, 1058) breaks when tools change format or output structure. Use machine-readable formats (JUnit XML, JSON, --output-format json) or native language features (pytest.mark.xfail, ruff's structured plugins) instead. Convergent finding across 3+ implementations.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
