---
name: crossprovider codex issue-scoped-commits-need-explicit-pathspecs-in-
description: Issue-scoped commits need explicit pathspecs in shared repositories
metadata:
  type: reference
  source: codex
  bridged: 2026-07-10
  tags: [git, workflow, multi-issue, pathspec]
---

When multiple issues are active in a single checkout/worktree, use explicit pathspecs in `git add` and `git commit` to restrict changes to issue-owned artifacts only. Prevents silent contamination of unrelated work and makes ownership boundaries explicit in commit history.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
