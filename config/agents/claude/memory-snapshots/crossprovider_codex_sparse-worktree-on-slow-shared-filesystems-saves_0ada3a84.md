---
name: crossprovider codex sparse-worktree-on-slow-shared-filesystems-saves
description: Sparse worktree on slow shared filesystems saves orders of magnitude
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [performance, filesystem, operations]
---

Full worktree checkout on slow mounts (observed: 104/22,875 files in multi-hour window) wastes session time. Sparse worktree with only the target paths completes in minutes. Use when applying focused changes to large repos on network/shared storage.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
