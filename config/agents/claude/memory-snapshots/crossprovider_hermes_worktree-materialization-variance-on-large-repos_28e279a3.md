---
name: crossprovider hermes worktree-materialization-variance-on-large-repos
description: Worktree materialization variance on large repos is timing hazard
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git, worktree, performance, large-repo]
---

workspace-hub 19K-file worktree: sometimes 17min, sometimes 1h+ stalled under parallel I/O. Recommend sanity-poll at 5min; if directory absent after timeout, kill+pivot to avoid doom-loop.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
