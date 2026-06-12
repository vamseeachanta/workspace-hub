---
name: crossprovider gemini bash-yaml-config-parsing-is-too-brittle
description: Bash YAML config parsing is too brittle
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [bash-antipattern, configuration, maintainability]
---

Bash regex-based YAML parsing breaks with indentation/formatting changes. Use yq CLI (lightweight YAML processor) or Python helper instead. Don't define config variables in .conf files if scripts don't actually consume them.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
