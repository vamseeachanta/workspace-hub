---
name: crossprovider codex inter-plan-dependencies-must-gate-or-expand-scop
description: Inter-plan dependencies must gate or expand scope
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning, multi-issue-coordination, scope-boundary]
---

When a plan depends on future work from sibling plans (e.g., #606 depends on #605's asset-resolver interface), either make it an explicit hard gate that blocks implementation, expand scope to implement both interfaces, or find a concrete workaround. Plans that say "when available" or assume future interfaces without gating are not implementable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
