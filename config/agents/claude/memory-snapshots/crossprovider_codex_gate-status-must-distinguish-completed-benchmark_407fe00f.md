---
name: crossprovider codex gate-status-must-distinguish-completed-benchmark
description: Gate status must distinguish: completed/benchmark-won, blocked-by-geometry, blocked-by-approval, not-ready-end-to-end
metadata:
  type: reference
  source: codex
  bridged: 2026-07-10
  tags: [gates, status, decision-making]
---

Cloudily saying 'blocked' masks different root causes (physics, authorization, incomplete implementation). Separating gate statuses makes recommendations actionable: don't rerun a completed benchmark, but do escalate a missing owner-approval. This taxonomy prevents wasted work and clarifies next steps.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
