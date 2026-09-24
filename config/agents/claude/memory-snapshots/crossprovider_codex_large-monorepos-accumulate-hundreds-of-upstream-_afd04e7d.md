---
name: crossprovider codex large-monorepos-accumulate-hundreds-of-upstream-
description: Large monorepos accumulate hundreds of upstream-gone branches requiring periodic audit
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [branch-hygiene, monorepo-maintenance, upstream-tracking]
---

Audit of llm-wiki found 187 upstream-gone local branches, workspace-hub had 24. Branches like `chore/llm-wiki-vision-verify-batch-{02..30...}` lose upstream tracking after PR merge and are never cleaned. Audit script: `git for-each-ref ... %(upstream:track)` or `git branch -vv | grep gone`. Systematic cleanup needed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
