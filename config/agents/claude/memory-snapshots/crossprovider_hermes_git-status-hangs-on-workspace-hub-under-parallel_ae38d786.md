---
name: crossprovider hermes git-status-hangs-on-workspace-hub-under-parallel
description: git status hangs on workspace-hub under parallel-agent load without GIT_OPTIONAL_LOCKS=0
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git, large-repo, parallel-load, workspace-hub, hermes]
---

19K+ file repo hangs on `git status` when multiple agents run in parallel; root cause is lock contention on `.git/index.lock`. Mitigate with `GIT_OPTIONAL_LOCKS=0 git status` or use `git status -uno` to reduce I/O.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
