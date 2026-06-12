---
name: crossprovider hermes worktree-materialization-variance-on-large-repos
description: Worktree materialization variance on large repos demands early sanity polling
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [worktree-perf, large-repo, agent-scheduling, overnight-batches]
---

19K-file workspace-hub worktree checkout times vary wildly: 17 min one run, 1h+ stalled another under parallel agent I/O. For unattended overnight lanes on large repos, sanity-check at ~5min; if the worktree directory is absent, kill the stalled agent and pivot. Avoid hard timeouts; detect stalls early via polling.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
