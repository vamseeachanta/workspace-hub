---
name: crossprovider codex narrow-searches-avoid-slowness-on-large-repos-wi
description: Narrow searches avoid slowness on large repos with generated state
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [performance, large-repos, tooling]
---

Broad text searches and full git status on repos with large mounted/generated corpus can timeout or produce noisy results. Narrow searches to specific directories (scripts/, tests/, docs/, coordination/) and use bounded commands (git grep, rg --files) instead of filesystem walks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
