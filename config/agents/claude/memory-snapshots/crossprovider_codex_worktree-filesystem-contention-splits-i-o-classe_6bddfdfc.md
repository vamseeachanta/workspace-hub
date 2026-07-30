---
name: crossprovider codex worktree-filesystem-contention-splits-i-o-classe
description: Worktree filesystem contention splits I/O classes
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [git, performance, filesystem]
---

Under sibling-session load, git operations (index, porcelain commands) hang while file-system reads/writes succeed. Use plain file access and output-captured verification when git is blocked.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
