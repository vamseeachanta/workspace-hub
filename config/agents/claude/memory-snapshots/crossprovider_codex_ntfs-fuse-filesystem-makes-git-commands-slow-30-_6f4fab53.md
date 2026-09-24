---
name: crossprovider codex ntfs-fuse-filesystem-makes-git-commands-slow-30-
description: NTFS-FUSE filesystem makes git commands slow (30–60s); this is normal
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, filesystem, performance, ntfs-fuse]
---

On NTFS-FUSE mounts (e.g., `/mnt/local-analysis/`), git commands routinely take 30–60 seconds. Use `GIT_OPTIONAL_LOCKS=0` and generous timeouts; be patient rather than retrying or investigating. This is not a fault—it is expected filesystem behavior.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
