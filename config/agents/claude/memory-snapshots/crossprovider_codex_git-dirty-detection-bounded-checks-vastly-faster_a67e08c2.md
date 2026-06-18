---
name: crossprovider codex git-dirty-detection-bounded-checks-vastly-faster
description: Git dirty detection: bounded checks vastly faster than status -uall
metadata:
  type: reference
  source: codex
  bridged: 2026-06-16
  tags: [git, performance, large-repo, optimization]
---

On repos with large untracked trees (workspace-hub, llm-wiki), `git status -uall` times out. Use `git diff --quiet && git diff --cached --quiet && git stash list` for dirty detection instead; orders of magnitude faster, sufficient for automation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
