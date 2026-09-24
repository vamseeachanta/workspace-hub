---
name: crossprovider codex scanner-blind-spots-with-untracked-files
description: Scanner blind spots with untracked files
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, testing, scanner-coverage]
---

`git diff --name-only` and `--diff-only` scanners miss untracked files entirely. To cover new files (tests, artifacts), use `git add -N <files>` to stage intent-to-add before running scanners, or include untracked-file checks in audit/coverage logic.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
