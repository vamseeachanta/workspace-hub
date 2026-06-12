---
name: crossprovider hermes git-lock-storms-under-parallel-load-use-git-opti
description: Git lock storms under parallel load; use GIT_OPTIONAL_LOCKS
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git, concurrency, performance, large-repo]
---

Long sessions with many parallel git processes (>20 git procs) accumulate zombie locks blocking commits. For commit-critical operations under load, use `GIT_OPTIONAL_LOCKS=0 git commit` to bypass advisory locks; pair with scoped pathspec commits (no `-A`) to avoid sweeping unrelated changes.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
