---
name: crossprovider codex classify-legacy-data-fixtures-vs-algorithm-repos
description: Classify legacy data fixtures vs. algorithm repositories
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, repository-structure, codebase-organization]
---

A directory is a data-fixture bundle (not a peer algorithm repo) if it lacks executable entry point, has only generated seed data and schemas, contains no package structure, and has zero inbound references from other modules. Useful for distinguishing code-review scope from architectural inventory.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
