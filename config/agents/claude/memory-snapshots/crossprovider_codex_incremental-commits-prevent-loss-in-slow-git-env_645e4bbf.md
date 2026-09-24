---
name: crossprovider codex incremental-commits-prevent-loss-in-slow-git-env
description: Incremental commits prevent loss in slow git environments
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, resilience, operations]
---

On NTFS-FUSE or slow filesystems (30–60s per git command), session timeouts during long operations will lose uncommitted work. Commit immediately after each test passes, not at the end of implementation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
