---
name: crossprovider gemini pytest-output-parsing-in-bash-is-fragile-use-str
description: Pytest output parsing in bash is fragile; use structured formats (JUnit XML or report-log)
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [testing, pytest, bash-limits]
---

Text-based stdout parsing breaks on pytest version updates, plugins, and edge cases (collection errors, timeouts). Leverage `--junitxml` or `--report-log` for resilient structured parsing.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
