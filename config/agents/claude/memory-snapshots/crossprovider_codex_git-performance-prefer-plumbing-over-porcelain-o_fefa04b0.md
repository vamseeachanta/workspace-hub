---
name: crossprovider codex git-performance-prefer-plumbing-over-porcelain-o
description: Git performance: prefer plumbing over porcelain on NTFS-FUSE
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, ntfs-fuse, performance]
---

`git status` can exceed 120s on NTFS-FUSE mounts. Use targeted plumbing commands instead: `git diff --name-only`, `git ls-remote`, `git show-ref`. Avoids full-tree scans and scales linearly with changed files, not tree size.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
