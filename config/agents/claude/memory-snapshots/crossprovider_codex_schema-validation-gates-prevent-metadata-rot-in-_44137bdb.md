---
name: crossprovider codex schema-validation-gates-prevent-metadata-rot-in-
description: Schema validation gates prevent metadata rot in work queues
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [governance, ci-cd, metadata]
---

Work item metadata quality (plan_reviewed, plan_approved, complexity, target_repos) improves measurably when schema validation gates are applied at commit/merge time. Gates must fail merges, not warn; warnings are ineffective.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
