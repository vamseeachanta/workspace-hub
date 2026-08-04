---
name: crossprovider codex slow-ntfs-fuse-requires-plumbing-git-commands-wi
description: Slow NTFS-FUSE requires plumbing git commands with generous timeouts
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [git, ntfs-fuse, performance, file-locking]
---

Porcelain git commands (`git status`) can exceed 120s on NTFS-FUSE mounts. Prefer targeted plumbing commands (e.g., `git ls-remote`, `git rev-parse`, `git diff`) with explicit timeouts. Interrupted git operations leave stale `.git/index.lock` files that must not be removed without checking for live processes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
