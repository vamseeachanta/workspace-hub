---
name: crossprovider gemini ci-orphan-cleanup-debt-after-large-migrations
description: CI orphan cleanup debt after large migrations
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [ci-health, migration-cleanup, infrastructure]
---

Large automated migrations (WRK→GSD sync) leave broken references in .pre-commit-config.yaml hook targets and .github/workflows/*.yml steps. Audit for dangling script refs post-migration; prune to unblock CI from collection errors.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
