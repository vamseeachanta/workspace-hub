---
name: crossprovider codex ntfs-filesystem-causes-git-status-git-diff-hangs
description: NTFS filesystem causes git status/git diff hangs; use direct file reads or ext4 mirrors
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [ntfs, filesystem, performance, git, workaround]
---

On NTFS-backed repository `/mnt/local-analysis`, `git status` and full `git diff` commands hang for minutes or timeout after ~60 seconds due to recursive inode traversal. Bounded reads (direct file I/O, Git plumbing queries, indexing-only `git diff-index`) work reliably. Workaround: use ext4 clones at `/tmp/` when available for performance-critical verification.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
