---
name: crossprovider hermes git-index-lock-contention-under-parallel-multi-a
description: Git index.lock contention under parallel multi-agent load blocks git status/commit operations
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-locking, parallel-load, contention]
---

Multiple sessions (2026-04-29 next-wave autofeed, approval-readiness monitors) reported `.git/index.lock` timeouts and status hangs under parallel fleet load. Stale locks can persist >5 minutes with zero holder process; recommend GIT_OPTIONAL_LOCKS=0 for status/log ops or pre-check lock age.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
