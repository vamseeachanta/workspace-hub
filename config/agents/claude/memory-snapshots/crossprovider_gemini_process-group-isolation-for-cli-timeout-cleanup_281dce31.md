---
name: crossprovider gemini process-group-isolation-for-cli-timeout-cleanup
description: Process group isolation for CLI timeout cleanup
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [process-management, shell-patterns, timeout-handling]
---

Wrap long-running CLI calls with `setsid timeout` to isolate into a process group, then kill with `kill -- -$pgid` on timeout. Set proper exit codes: 0=success, 124=timeout, 1=other. Prevents subprocess leaks and zombie processes from timeout interactions.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
