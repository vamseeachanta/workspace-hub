---
name: crossprovider hermes post-commit-hooks-regenerate-tracked-files-re-ch
description: Post-commit hooks regenerate tracked files; re-check status after closeout commits
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hooks, git-workflow, closeout-discipline]
---

Workspace-hub post-commit hooks update `.claude/state/*` and other generated files. After a closeout/ledger commit, you must re-run `git status` bounded to check for newly staged/modified files before declaring root clean. Skipping this leads to stale open commits.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
