---
name: crossprovider codex use-git-show-path-to-isolate-staged-scope-in-dir
description: Use git show :path to isolate staged scope in dirty worktrees
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, staging, scope-isolation, review]
---

`git show :path` reads staged blobs directly from the index, bypassing filesystem drift. When staged content must be reviewed and the worktree has unstaged changes, this prevents review evidence from being contaminated by uncommitted modifications.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
