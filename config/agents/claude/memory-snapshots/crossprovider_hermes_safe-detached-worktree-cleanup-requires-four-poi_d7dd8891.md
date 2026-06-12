---
name: crossprovider hermes safe-detached-worktree-cleanup-requires-four-poi
description: Safe detached worktree cleanup requires four-point verification
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [worktree-cleanup, git-safety, process-liveness]
---

Only remove a detached worktree after confirming: (1) no active process CWD inside, (2) `unique_origin_main = 0` (no unmerged commits), (3) HEAD ancestor of origin/main, (4) clean working status. Skipping any check risks losing valid work or orphaning commits.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
