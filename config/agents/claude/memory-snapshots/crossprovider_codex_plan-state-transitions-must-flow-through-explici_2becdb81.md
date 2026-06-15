---
name: crossprovider codex plan-state-transitions-must-flow-through-explici
description: Plan state transitions must flow through explicit approval gates
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [governance, approval-gates, workflow]
---

Issues flow through `pending` → `plan-review` → `plan-approved` gates explicitly; user approval is a gate, not implicit from parent approval. Child issues need separate approval boundaries unless plan explicitly scopes child execution. Dependency links in live GitHub must match plan pseudocode execution order.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
