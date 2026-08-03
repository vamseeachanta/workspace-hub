---
name: crossprovider codex pytest-discovery-hangs-on-ntfs-fuse-worktrees-td
description: Pytest discovery hangs on NTFS-FUSE worktrees; TDD requires /tmp harness
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [testing, fuse, worktree, performance, tdd]
---

Pytest's file discovery can hang when running on NTFS-FUSE mounted worktrees. Solution: write tests in /tmp, byte-compare them against the worktree to confirm they match, then run the /tmp harness standalone. This decouples test development from FUSE's file-walk performance.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
