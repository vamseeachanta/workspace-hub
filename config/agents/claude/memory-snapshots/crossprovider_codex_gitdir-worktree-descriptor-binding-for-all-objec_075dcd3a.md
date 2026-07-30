---
name: crossprovider codex gitdir-worktree-descriptor-binding-for-all-objec
description: Gitdir/worktree descriptor binding for all object reads
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [security, git, descriptor-security]
---

All Git object commands must carry both bound worktree + gitdir file descriptors + inherited FDs. Don't use bare `git -C` after initial resolution. Binds authority at operation boundary, not just file-open.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
