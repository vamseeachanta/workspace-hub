---
name: crossprovider codex pathspec-commits-don-t-auto-stage-untracked-file
description: Pathspec commits don't auto-stage untracked files
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-workflow, pathspec-commits]
---

Using `git commit -m "..." -- <file>` for isolated branching requires pre-staging with `git add <file>` first; pathspec alone does not add untracked files to the index. Verify staged set before committing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
