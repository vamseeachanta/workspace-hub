---
name: crossprovider codex exit-trap-on-local-variables-doesn-t-work-as-exp
description: EXIT trap on local variables doesn't work as expected
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [bash, cleanup, trap, scope]
---

EXIT traps fire after the function scope ends, but local variables are already deallocated. For temp directories, use explicit cleanup at function end or early returns — don't rely on trap-based cleanup for function-local state.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
