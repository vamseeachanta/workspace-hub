---
name: crossprovider gemini uv-run-command-v-incompatibility
description: uv run command -v incompatibility
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [shell-scripting, tooling, python, uv, refactoring-hazard]
---

`command -v` shell builtin accepts only a single command name and rejects compound invocations like `uv run --no-project python`. Bulk sed replacements of `python3` → `uv run --no-project python` in shell scripts will break detection logic. Use surgical per-script replacement: detection paths get `command -v uv`, execution paths get the compound command only for scripts that don't manage their own venvs.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
