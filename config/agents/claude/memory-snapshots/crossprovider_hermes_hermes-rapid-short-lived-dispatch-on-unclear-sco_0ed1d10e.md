---
name: crossprovider hermes hermes-rapid-short-lived-dispatch-on-unclear-sco
description: Hermes rapid short-lived dispatch on unclear scope signals misalignment
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes-dispatch, task-clarity]
---

Hermes spawned 11+ sessions in ~25min (timestamps 04:45–05:09) on #2665 without convergence; sessions averaged ~2min and all re-entered intake. Likely indicators: task scope exceeds single-agent decomposition, or skill framework (kanban-orchestrator, hermes-agent) was incomplete/misaligned. Staged dispatch (intake-only card → plan-only card → review-only card) with explicit exit gates reduces session thrash.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
