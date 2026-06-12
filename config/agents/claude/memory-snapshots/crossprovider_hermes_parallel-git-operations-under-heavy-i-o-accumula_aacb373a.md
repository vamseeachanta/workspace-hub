---
name: crossprovider hermes parallel-git-operations-under-heavy-i-o-accumula
description: Parallel git operations under heavy I/O accumulate zombie status processes
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-internals, parallel-load, lock-contention, multi-agent]
---

Long sessions with 3+ concurrent agents spawn many `git status -z` calls. Under contention, some block commit locks for minutes. Unblock via `GIT_OPTIONAL_LOCKS=0 git commit <pathspec>` with explicit pathspec; afterwards check stale `.git/index.lock` and `git status` output.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
