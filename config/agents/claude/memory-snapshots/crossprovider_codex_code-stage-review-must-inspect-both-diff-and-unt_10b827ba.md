---
name: crossprovider codex code-stage-review-must-inspect-both-diff-and-unt
description: Code-stage review must inspect both diff and untracked artifacts
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [code-review, git-workflow, artifacts]
---

A branch can commit only metadata (plan status) while hiding real code/generated outputs as untracked files. Worktree inspection must check both `git diff origin/main...HEAD` AND filesystem `find`/`ls` for generated artifacts, or require implementation tracked before merge.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
