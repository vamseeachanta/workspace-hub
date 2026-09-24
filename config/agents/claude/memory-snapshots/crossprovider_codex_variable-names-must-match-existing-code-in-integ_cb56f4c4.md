---
name: crossprovider codex variable-names-must-match-existing-code-in-integ
description: Variable names must match existing code in integration points
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [integration, shell, variable-scope]
---

When integrating new code into existing scripts (e.g., calling a new utility from work.sh), verify variable names match what's already defined in that script. Use `grep` on the target file before assuming SCRIPT_DIR, AGENTS_DIR, or other conventions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
