---
name: crossprovider codex unconstrained-pkill-f-patterns-can-match-invokin
description: Unconstrained `pkill -f` patterns can match invoking shell chain
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [shell-safety, process-management]
---

Regex patterns like `pkill -f 'rg -n pattern|...'` match parent/shell process arguments when that command is still running. Session-level code should use explicit PIDs, process-name anchors, or rely on harness-level mitigations (`</dev/null`). Unsafe termination is self-inflicting (process flood → pkill → session death).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
