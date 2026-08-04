---
name: crossprovider codex ntfs-fuse-unsuitable-for-git-work-surfaces
description: NTFS-FUSE unsuitable for git work surfaces
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [infrastructure, filesystem, git-ops]
---

NTFS-FUSE (fuseblk) lacks POSIX permissions and causes git porcelain to stall, breaking enforcement gates that depend on `.git/hooks/`. Work surfaces should use native filesystems like ext4.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
