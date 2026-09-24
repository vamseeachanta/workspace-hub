---
name: crossprovider codex ntfs-fuse-mounts-cannot-safely-run-git-operation
description: NTFS-FUSE mounts cannot safely run git operations
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [filesystem, git, environment-constraint]
---

Git commands on NTFS-FUSE mounts stall or fail. When working in such environments, use filesystem and GitHub evidence only for verification; never attempt git add/commit/push from the mount point.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
