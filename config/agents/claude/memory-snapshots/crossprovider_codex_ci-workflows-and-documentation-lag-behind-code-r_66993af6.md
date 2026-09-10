---
name: crossprovider codex ci-workflows-and-documentation-lag-behind-code-r
description: CI workflows and documentation lag behind code refactors
metadata:
  type: reference
  source: codex
  bridged: 2026-07-30
  tags: [refactoring, ci-maintenance, documentation-sync, published-api]
---

After directory moves and module extraction, CI workflows continue watching deleted paths, documentation still lists removed files, and published extras break external consumers. Sync CI path filters, workflow definitions, documentation references, and packaging extras in the same commit as the refactor or flag explicitly in review.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
