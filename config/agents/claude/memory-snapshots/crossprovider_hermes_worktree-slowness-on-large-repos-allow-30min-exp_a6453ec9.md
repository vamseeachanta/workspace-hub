---
name: crossprovider hermes worktree-slowness-on-large-repos-allow-30min-exp
description: Worktree slowness on large repos: allow 30min, expect 60% timeout risk
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [worktree, performance, large-repos]
---

Creating a worktree on workspace-hub (33K files) materializes in 17min–1h+ under parallel I/O load. Sanity-poll at 5min; if absent after that, kill and pivot. Use worktrees only when git-lock contention is unavoidable (execution-only runs), not for planning.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
