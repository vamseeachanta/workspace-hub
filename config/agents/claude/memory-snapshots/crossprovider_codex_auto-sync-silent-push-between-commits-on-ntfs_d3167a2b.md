---
name: crossprovider codex auto-sync-silent-push-between-commits-on-ntfs
description: Auto-sync silent push between commits on NTFS
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, ntfs-fuse, hazard, autosync]
---

Git auto-sync can push intermediate commits before a full multi-commit sequence completes, bypassing the developer's intended atomicity. On NTFS-FUSE mounts, verify push success with `git ls-remote origin <branch>` (not exit codes), and check the branch file-list (`git diff --name-only origin/main...HEAD`) for swept unrelated files before opening PRs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
