---
name: crossprovider hermes git-safety-under-heavy-parallel-load-git-optiona
description: Git safety under heavy parallel load: GIT_OPTIONAL_LOCKS=0 + short timeouts
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-patterns, performance, parallel-work, environment-tuning]
---

Under heavy parallel-git load (multi-session, >20 git processes), use `GIT_OPTIONAL_LOCKS=0 git commit` to bypass lock contention, apply short timeouts (~30s) on status/log/worktree commands, and check reflog for silent reverts. Long git-status queries with `-uall` can accumulate zombie processes and block commits.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
