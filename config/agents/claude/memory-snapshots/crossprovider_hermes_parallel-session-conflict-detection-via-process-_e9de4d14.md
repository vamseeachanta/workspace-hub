---
name: crossprovider hermes parallel-session-conflict-detection-via-process-
description: Parallel session conflict detection via process, not file state
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [parallel-agents, liveness, process-detection]
---

Multiple agents can run in parallel on same repo. Detect active sessions via `pgrep` for live worker processes, not by checking `.git/index.lock` or file state. Hermes `active_agents` and Codex index are history-only; inspect process table for true liveness.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
