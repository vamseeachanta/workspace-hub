---
name: crossprovider codex bash-local-keyword-can-only-be-used-inside-funct
description: Bash local keyword can only be used inside functions
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [bash, scoping, common-error]
---

The `local` keyword in bash produces `local: can only be used in a function` error when used at script top-level. Common mistake when refactoring argument parsing or copy-pasting function bodies; use simple variable assignment at top level instead.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
