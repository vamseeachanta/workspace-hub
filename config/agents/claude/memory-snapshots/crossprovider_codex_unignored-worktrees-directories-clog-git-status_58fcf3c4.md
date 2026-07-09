---
name: crossprovider codex unignored-worktrees-directories-clog-git-status
description: Unignored .worktrees/ directories clog git status
metadata:
  type: reference
  source: codex
  bridged: 2026-07-08
  tags: [git-hygiene, performance, gitignore]
---

Projects creating `.worktrees/` subdirectories but not excluding them from `.gitignore` cause `git status` to crawl thousands of untracked files. Use `git diff HEAD` (tracked-only) or `--porcelain` to avoid I/O noise; inherited residue in shared checkouts is common.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
