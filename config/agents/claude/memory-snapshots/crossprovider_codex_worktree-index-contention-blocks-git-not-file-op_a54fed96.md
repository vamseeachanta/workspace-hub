---
name: crossprovider codex worktree-index-contention-blocks-git-not-file-op
description: Worktree index contention blocks Git, not file ops
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [performance, git, multi-session]
---

Under multi-session load on large repositories (2.6+ MB indexes), Git commands timeout while plain file access remains responsive. During contention, use output-captured verification, read-only audits, and file-only operations. Retry Git after sibling processes exit.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
