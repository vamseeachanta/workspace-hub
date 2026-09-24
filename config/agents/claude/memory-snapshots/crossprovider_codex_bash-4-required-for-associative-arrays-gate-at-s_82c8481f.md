---
name: crossprovider codex bash-4-required-for-associative-arrays-gate-at-s
description: Bash 4+ required for associative arrays; gate at startup
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [bash, version-gating, compatibility, error-handling]
---

Use `if (( BASH_VERSINFO[0] < 4 ))` at function entry to reject incompatible shells early. Emit error to stderr and use `return 1 2>/dev/null || exit 1` to handle both sourced (return) and standalone (exit) contexts gracefully.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
