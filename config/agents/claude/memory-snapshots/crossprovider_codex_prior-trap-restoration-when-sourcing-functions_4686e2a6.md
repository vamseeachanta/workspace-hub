---
name: crossprovider codex prior-trap-restoration-when-sourcing-functions
description: Prior trap restoration when sourcing functions
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [bash, trap-handling, sourcing]
---

Save caller's EXIT trap before installing your own: _prior_exit_trap="$(trap -p EXIT 2>/dev/null || true)". Restore at end of function. Prevents clobbering when a script is sourced (not exec'd), critical for multi-layer sourcing chains.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
