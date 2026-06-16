---
name: crossprovider codex process-discovery-requires-cwd-checking-not-just
description: Process discovery requires CWD checking, not just ps output
metadata:
  type: reference
  source: codex
  bridged: 2026-06-15
  tags: [parallel-work, process-discovery, timeouts, repo-contention]
---

ps output alone does not prove that a process is contending for a specific repository. Check actual process working directories. Use bounded timeouts on repo operations (git, grep) to avoid hanging behind other work; stalled operations block closeout.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
