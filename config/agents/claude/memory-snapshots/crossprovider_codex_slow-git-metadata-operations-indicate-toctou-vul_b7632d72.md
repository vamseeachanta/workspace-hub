---
name: crossprovider codex slow-git-metadata-operations-indicate-toctou-vul
description: Slow Git metadata operations indicate TOCTOU vulnerability; re-verify before commit
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [git, concurrency, filesystem]
---

When `git status` or `git add` are slow (NTFS-FUSE, large .git, network mounts), the shared index is a time-of-check-to-time-of-use surface. Stale entries can invalidate prior checks. Re-fetch and re-verify immediately before commit.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
