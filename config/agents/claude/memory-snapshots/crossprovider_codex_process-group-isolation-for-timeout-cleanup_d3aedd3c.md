---
name: crossprovider codex process-group-isolation-for-timeout-cleanup
description: Process group isolation for timeout cleanup
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [timeout-handling, process-lifecycle, exit-codes]
---

Use `setsid` to launch long-running processes in their own process group. On timeout, send SIGTERM to the full group (not just parent), sleep 1s for graceful shutdown, then SIGKILL. Propagate exit code 124 for timeout (distinct from 1 for other failures) so callers can distinguish and handle differently.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
