---
name: crossprovider codex pathspec-commits-isolate-changes-in-noisy-worktr
description: Pathspec commits isolate changes in noisy worktrees
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, worktree-hygiene, commit-isolation]
---

When a worktree has pre-existing staged deletions or missing tracked files, use `git commit -m "message" --only -- <file1> <file2>` (note: message argument before `--only` and pathspec) to commit only target files and avoid sweeping unrelated staged changes into the commit.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
