---
name: crossprovider codex per-repo-error-capture-prevents-early-script-abo
description: Per-repo error capture prevents early script abort — use if-wrapped commands, not set -e
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [shell-patterns, error-handling]
---

In multi-repo loops, wrap each command with error capture: `result=$(cmd 2>&1); rc=$?; if [[ $rc -ne 0 ]]; then record_error; fi`. Never call `exit` inside the repo loop. This ensures all repos are processed even if some fail.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
