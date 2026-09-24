---
name: crossprovider codex exit-only-traps-in-sourced-functions-avoid-bash-
description: EXIT-only traps in sourced functions avoid bash abort override
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [bash, trap-handling, sourced-functions, signal-handling]
---

Trapping INT/TERM in a sourced function overrides bash's default abort behavior — the handler runs, then execution continues instead of exiting. Solution: trap EXIT only; on Ctrl+C bash naturally exits and fires the EXIT trap on the way out. Further refinement: use `trap -p EXIT` to save and restore the caller's prior trap, avoiding clobbering when the function is sourced.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
