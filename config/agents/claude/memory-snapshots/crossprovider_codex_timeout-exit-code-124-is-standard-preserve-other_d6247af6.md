---
name: crossprovider codex timeout-exit-code-124-is-standard-preserve-other
description: Timeout exit code 124 is standard; preserve other exit codes
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [bash-error-handling, timeout, exit-codes]
---

When wrapping commands with `timeout`, distinguish exit code 124 (timeout fired) from other non-zero codes (actual failure). Gate handlers must check `if [[ $exit -eq 124 ]]` separately and not blanket-trap all non-zero exits, or you'll misclassify actual failures as timeouts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
