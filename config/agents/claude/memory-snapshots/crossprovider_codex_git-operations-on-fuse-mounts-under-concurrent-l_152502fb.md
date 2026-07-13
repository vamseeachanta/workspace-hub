---
name: crossprovider codex git-operations-on-fuse-mounts-under-concurrent-l
description: Git operations on FUSE mounts under concurrent load need targeted reads, not full scans
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [git, fuse, concurrency, performance]
---

Full git status calls hang under concurrent load on fuseblk; allow index locks to release naturally. Use plumbing commands (git show, pathspec commits) and avoid broad repository scans when concurrent operations are active.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
