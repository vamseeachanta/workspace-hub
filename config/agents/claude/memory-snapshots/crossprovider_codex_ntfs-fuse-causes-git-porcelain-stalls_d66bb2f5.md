---
name: crossprovider codex ntfs-fuse-causes-git-porcelain-stalls
description: NTFS-FUSE causes git porcelain stalls
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [filesystem, git, storage-architecture, performance]
---

NTFS-FUSE (common in external/network drives) lacks POSIX permissions and reliable hardlinks, causing git porcelain commands to hang and stall. Work surfaces for active git operations should use ext4 or native filesystems; NTFS-FUSE is suitable only for long-term data storage, not development.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
