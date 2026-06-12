---
name: crossprovider hermes pre-bridge-memory-sync-fails-on-untracked-files-
description: Pre-bridge memory sync fails on untracked files; recover via stash pathspec
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git, memory-sync, error-recovery]
---

Pre-bridge quality scripts fail when untracked files exist in working tree. Recovery: `git checkout stash@{0} -- .claude/memory` to extract memory dir from stash, then commit. Applies to Git-based memory systems without force-flag bridges.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
