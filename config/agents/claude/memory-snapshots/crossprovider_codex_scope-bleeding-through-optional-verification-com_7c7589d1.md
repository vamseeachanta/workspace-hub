---
name: crossprovider codex scope-bleeding-through-optional-verification-com
description: Scope-bleeding through optional verification commands
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning, review, scope-control]
---

When a plan excludes a domain (e.g., 'we don't touch query/navigation'), check optional or fallback verification steps for escape hatches. Commands like optional graph regeneration can mutate domains they're not supposed to touch, violating stated scope boundaries.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
