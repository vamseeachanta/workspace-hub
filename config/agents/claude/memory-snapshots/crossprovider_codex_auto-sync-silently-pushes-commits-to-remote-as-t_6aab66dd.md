---
name: crossprovider codex auto-sync-silently-pushes-commits-to-remote-as-t
description: Auto-sync silently pushes commits to remote as they land locally
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [git, auto-sync, ntfs-fuse, verification]
---

On NTFS-FUSE mounts, auto-sync commits appear on the remote branch before the full local commit sequence completes. Pushing subsequent commits may race with prior silent pushes. Always verify branch HEAD with `git ls-remote origin <branch>` after each commit, not just the push command's exit code.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
