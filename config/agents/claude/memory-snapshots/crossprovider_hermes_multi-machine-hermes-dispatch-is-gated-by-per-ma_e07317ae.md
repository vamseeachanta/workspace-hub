---
name: crossprovider hermes multi-machine-hermes-dispatch-is-gated-by-per-ma
description: Multi-machine Hermes dispatch is gated by per-machine readiness classification
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, dispatch, readiness, multi-machine]
---

Machines fall into three classes: `dispatch_enabled=true` (requires full readiness check + workspace clean + Hermes running), `dispatch_enabled=false` (status-only, safe for inventory/monitoring), and `not_onboarded` (no workspace root yet). Readiness audit output has structured format: `overall_status`, per-machine failures, and specific blockers.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
