---
name: crossprovider codex ntfs-large-worktree-pathology-switch-to-path-bou
description: NTFS large-worktree pathology: switch to path-bounded I/O
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ntfs, performance, worktree-operations]
---

Large NTFS checkouts can hang indefinitely on `git status` or recursive traversal. Workaround: use path-bounded reads, direct file I/O, and ext4 clones for fallback comparisons.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
