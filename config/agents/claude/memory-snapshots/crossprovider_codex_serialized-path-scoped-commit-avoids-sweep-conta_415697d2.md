---
name: crossprovider codex serialized-path-scoped-commit-avoids-sweep-conta
description: Serialized path-scoped commit avoids sweep contamination
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, operations, parallel-agents]
---

When parallel agents race on a shared Git index, use `git commit -m "..." -- <file1> <file2>` with explicit pathspec to stage only intended paths. Prevents accidental inclusion of unrelated worktree edits that may have landed between stages. Codex #3384 used this to isolate 7 Task 1 paths while preserving pre-existing untracked `.superpowers/` content.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
