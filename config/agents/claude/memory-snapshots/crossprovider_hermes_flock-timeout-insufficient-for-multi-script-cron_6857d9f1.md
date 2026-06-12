---
name: crossprovider hermes flock-timeout-insufficient-for-multi-script-cron
description: Flock timeout insufficient for multi-script cron contention
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cron-scheduling, git-locking, contention]
---

gsd-researcher (01:35) uses flock /tmp/workspace-hub-git.lock with 120s timeout, but comprehensive-learning-nightly (02:00) does unlocked git ops with ~1 hour runtime. They race: comprehensive-learning pushes while gsd-researcher might still hold flock, then unlocked push tries anyway. Need either script-level deduplication (PID-file lock on script itself) or global flock covering all workspace-hub git ops.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
