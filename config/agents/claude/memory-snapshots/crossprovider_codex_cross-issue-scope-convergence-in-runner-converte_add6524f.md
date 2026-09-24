---
name: crossprovider codex cross-issue-scope-convergence-in-runner-converte
description: Cross-issue scope convergence in runner/converter paths
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, scope-planning, multi-issue-coordination]
---

Multiple OrcaWave issues (#500, #605–608) converge on the same runner and converter implementation paths. When plan-approved and draft plans touch overlapping surfaces, the first implementation must either extract shared helpers into a unified resolver or establish explicit ordering to avoid maintaining parallel paths. Failing to reconcile upfront causes duplicate implementations and later refactoring debt.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
