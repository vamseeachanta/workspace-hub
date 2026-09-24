---
name: crossprovider codex multi-agent-tmp-cleanup-is-risky-without-live-pr
description: Multi-agent /tmp cleanup is risky without live-process enumeration
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [system-maintenance, multi-agent-safety, cleanup, concurrency]
---

Active session worktrees from parallel agents contaminate /tmp even after appearing disposable. Safe cleanup requires enumerating actual live processes, using flock overlap protection, and measuring pressure thresholds rather than pattern-based deletion. Deleting clean-looking worktrees can break concurrent sessions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
