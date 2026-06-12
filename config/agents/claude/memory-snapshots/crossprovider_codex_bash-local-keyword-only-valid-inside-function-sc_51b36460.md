---
name: crossprovider codex bash-local-keyword-only-valid-inside-function-sc
description: Bash `local` keyword only valid inside function scope
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [shell-syntax, bash-gotchas, scoping]
---

Using `local` at script top level or in conditionals raises "local: can only be used in a function" and crashes script. Use `local` only inside function bodies; use plain variable assignment at module scope.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
