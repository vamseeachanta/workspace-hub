---
name: crossprovider codex bash-local-keyword-only-valid-inside-function-sc
description: Bash `local` keyword only valid inside function scope
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [bash, scripting, syntax]
---

Session 12 found test-task.sh crashed immediately with 'local repo_name=... local: can only be used in a function' error. Bash `local` at top-level is invalid; use plain variable assignment or move to function.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
