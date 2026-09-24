---
name: crossprovider codex git-worktree-hygiene-use-pathspec-scoped-status-
description: Git worktree hygiene: use pathspec-scoped status and commits to isolate issue work from pre-existing noise
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-ops, worktree-hygiene, pathspec-scoping]
---

Multiple worktrees accumulate unrelated files (untracked prompt artifacts, coverage results, stashes) that interfere with clean issue commits. Use `git status -- <owned-paths>` and `git commit -m "..." -- <file1> <file2>` to stage/commit only the intended files, avoiding accidental sweeps of sibling-repo state or pre-existing worktree debris.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
