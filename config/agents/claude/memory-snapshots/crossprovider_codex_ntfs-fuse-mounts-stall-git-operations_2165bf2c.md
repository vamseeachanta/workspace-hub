---
name: crossprovider codex ntfs-fuse-mounts-stall-git-operations
description: NTFS-FUSE mounts stall git operations
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [filesystem-constraints, environment]
---

NTFS-FUSE mounts are unsuitable for git workflows — git operations hang or fail. Use ext4 native clones or native filesystems when git access is required. This is a hard constraint affecting tool and workflow selection.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
