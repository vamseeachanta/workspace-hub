---
name: crossprovider codex git-diff-on-mnt-local-analysis-hangs-on-large-bi
description: Git diff on /mnt/local-analysis hangs on large binaries
metadata:
  type: reference
  source: codex
  bridged: 2026-07-08
  tags: [git, performance, large-repos, debugging]
---

Avoid broad `git diff --stat` or `rg --files` on `/mnt/local-analysis` root; scope to target repo or use `git status` plus targeted reads. The mount traverses large binary/data artifacts and hangs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
