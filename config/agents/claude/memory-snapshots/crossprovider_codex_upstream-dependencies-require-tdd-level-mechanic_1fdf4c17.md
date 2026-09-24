---
name: crossprovider codex upstream-dependencies-require-tdd-level-mechanic
description: Upstream dependencies require TDD-level mechanical enforcement, not just issue-label checking
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning, dependencies, TDD, multi-issue-workflows]
---

When issue #267 depends on #266 (e.g., taxonomy artifacts), checking only that #266 is `status:plan-approved` is insufficient—the #267 TDD must verify live artifact existence with provenance markers (e.g., `source_issue: 266`, schema version) at test time. Label-only gating defers risk to implementation and allows scope creep.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
