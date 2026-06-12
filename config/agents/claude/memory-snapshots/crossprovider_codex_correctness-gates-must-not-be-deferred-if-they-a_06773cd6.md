---
name: crossprovider codex correctness-gates-must-not-be-deferred-if-they-a
description: Correctness gates must not be deferred if they affect primary scope
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [scope, deferral, risk-acceptance]
---

Deferring validation items (e.g., workflow schema checks) when the issue explicitly targets restoring CI leaves critical integrity outside the gate. Deferred items in the critical path need explicit acknowledgment as residual risk and stronger justification than arbitrary thresholds.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
