---
name: crossprovider codex distributed-locks-in-shell-scripts-require-atomi
description: Distributed locks in shell scripts require atomic delete and pre-execution verification
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [shell, concurrency, distributed-systems, locking]
---

Shell-based distributed locks are vulnerable to race conditions without careful fencing: same-host processes can both acquire the same lease if holder identifiers aren't unique per dispatcher; delete operations race if not atomic (compare-and-set fenced); execution can proceed with a superseded lease. Mitigate with: unique holder identifiers per dispatcher, atomic CAS delete, and lease verification immediately before execution.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
