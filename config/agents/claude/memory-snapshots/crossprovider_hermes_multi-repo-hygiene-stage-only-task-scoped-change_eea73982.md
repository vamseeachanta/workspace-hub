---
name: crossprovider hermes multi-repo-hygiene-stage-only-task-scoped-change
description: Multi-repo hygiene: stage only task-scoped changes per repo
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-hygiene, multi-repo, staging]
---

When fixing CI/test issues across nested repos, carefully inventory pre-existing dirty state and untracked files per repo. Stage and commit only task-owned patches; avoid bulk-staging unrelated generated artifacts. Use `git status --porcelain` and `git diff --name-only` to review diffs before staging per repo.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
