---
name: crossprovider codex ntfs-fuse-is-unsuitable-for-git-operations-and-b
description: NTFS-FUSE is unsuitable for git operations and bulk data
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [infrastructure, filesystem, git]
---

NTFS-FUSE (fuseblk) lacks POSIX permissions, reliable hardlinks, and has a documented history of git porcelain stalling on the fleet's machines. Work surfaces on NTFS-FUSE should hold only git repos and live worktrees; bulk data must be relocated to ext4 substrates (e.g., /mnt/ace).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
