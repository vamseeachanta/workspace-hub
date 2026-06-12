---
name: crossprovider hermes large-repo-git-status-commands-timeout-use-bound
description: Large-repo git status commands timeout; use bounded checks
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-perf, workspace-management]
---

`bash scripts/repository_sync status work` times out after ~300s on repos with 30K+ tracked files (e.g., workspace-hub). Replace with bounded alternatives: `git diff --name-only`, `git diff --cached --name-only`, `--untracked-files=no`, or `git ls-files --others --exclude-standard | head` for faster feedback on large repos.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
