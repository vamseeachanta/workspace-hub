---
name: crossprovider codex quality-harness-failure-reporting-must-surface-u
description: Quality harness failure reporting must surface underlying tool output, not just error counts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [error-handling, debuggability, validation-harness]
---

Reporting `FAIL (0 errors)` when a tool exits with failure code due to config/env issues is worse than no information. Always print the tool's stderr/stdout when exit codes indicate failure. If parsing cannot extract error counts (due to environment failure), report the unparseable output instead of a false count.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
