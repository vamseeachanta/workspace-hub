---
name: crossprovider codex sparse-cone-mode-git-worktrees-index-refresh-is-
description: Sparse cone-mode git worktrees: index refresh is the bottleneck on slow mounts
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [git-worktree, slow-mount, ntfs-fuse, performance]
---

On NTFS-FUSE mounts, full `git worktree add` hangs during initial 22,689-file checkout. Sparse cone-mode mitigates by materializing only selected paths (~235 files), but a single redundant `git checkout` still triggers full 22,689-entry index refresh. Move sparse worktrees to `/tmp` (local metadata) once registered to avoid repeated index rebuilds.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
