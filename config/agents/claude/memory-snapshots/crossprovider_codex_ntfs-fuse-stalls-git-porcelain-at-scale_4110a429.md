---
name: crossprovider codex ntfs-fuse-stalls-git-porcelain-at-scale
description: NTFS-FUSE stalls git porcelain at scale
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [filesystem, operational-constraint, git-scale, ntfs-fuse]
---

NTFS-FUSE filesystem backing for 100+ git repos causes documented git command stalling. Filesystem substrate is an operational constraint, not an afterthought. Large batch git operations (dispatch, multi-repo scans) fail or hang on NTFS-FUSE.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
