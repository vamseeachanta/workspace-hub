---
name: crossprovider codex bash-4-version-check-for-associative-arrays-with
description: Bash 4+ version check for associative arrays with dual-context exit
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [bash, version-check, sourcing]
---

Scripts using `declare -A` require Bash 4+. Check `(( BASH_VERSINFO[0] < 4 ))` at top of sourced scripts. Use `return 1 2>/dev/null || exit 1` to handle both sourced contexts (return exits gracefully) and direct execution (exit stops script).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
