---
name: crossprovider hermes temp-file-cleanup-traps-don-t-run-under-set-e-ab
description: Temp-file cleanup traps don't run under set -e abort
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [shell-safety, trap-semantics, bug-pattern]
---

In shell scripts with `set -e`, a failed command (e.g., jq parse error) aborts before reaching the cleanup trap/return block. sync-agent-configs.sh had a JSON merge path that left temp files on jq failure because the error exited the function before the cleanup trap. Wrap risky commands in `|| false` or use `trap` on the subshell to guarantee cleanup runs.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
