---
name: crossprovider hermes git-status-timeout-on-large-repos-use-bounded-st
description: Git status timeout on large repos—use bounded status flags instead of full scan
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-status, large-repo, performance]
---

On workspace-hub (33K files), `git status` without flags or `git status -uall` can timeout (>300s). Use `git status --untracked-files=no`, `git diff --name-only`, `git diff --cached --name-only`, or `git ls-files --others --exclude-standard | head` for faster bounded checks.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
