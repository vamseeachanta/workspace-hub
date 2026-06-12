---
name: crossprovider hermes repo-by-repo-execution-requires-scoped-staging-d
description: Repo-by-repo execution requires scoped staging discipline
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-hygiene, staging, multi-repo, commit-discipline]
---

Inventory dirty state FIRST across all repos, then stage only owned changes per repo. Never stage unrelated session/generated files (data/*, .claude/*, stats.json, cache, GTM demo outputs). This prevents accidental commits of churn. Re-check for hook-generated dirt after each commit.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
