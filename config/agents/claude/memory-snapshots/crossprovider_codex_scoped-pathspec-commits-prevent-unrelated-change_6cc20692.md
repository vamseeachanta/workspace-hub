---
name: crossprovider codex scoped-pathspec-commits-prevent-unrelated-change
description: Scoped pathspec commits prevent unrelated-change sweep
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [git-discipline, collaboration]
---

Use explicit `git add <path1> <path2>` and `git commit` rather than `git add -A` when other sessions are active. This prevents accidentally pulling in unrelated staged changes or uncommitted work that may be in flight.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
