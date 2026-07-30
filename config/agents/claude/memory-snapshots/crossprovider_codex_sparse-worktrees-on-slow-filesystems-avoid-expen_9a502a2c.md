---
name: crossprovider codex sparse-worktrees-on-slow-filesystems-avoid-expen
description: Sparse worktrees on slow filesystems avoid expensive full-tree scans
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [git, performance, filesystem, large-repos]
---

Full-tree git status and corpus scans on slow mounts (NTFS-FUSE, mounted storage) bottleneck discovery. Use sparse checkouts for planning/documentation-only work to materialize only needed paths.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
