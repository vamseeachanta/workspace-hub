---
name: crossprovider codex worktree-filesystem-matters
description: Worktree filesystem matters
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, filesystems, worktrees]
---

Implementation worktrees must use ext4, not NTFS-FUSE mounts. NTFS-FUSE breaks git commit/stash/reflog operations, forcing workaround patterns that create cleanup debt and prevent clean state verification.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
