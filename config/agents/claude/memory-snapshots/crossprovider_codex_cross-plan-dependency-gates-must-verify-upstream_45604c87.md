---
name: crossprovider codex cross-plan-dependency-gates-must-verify-upstream
description: Cross-plan dependency gates must verify upstream artifact scope
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cross-plan-dependencies, gate-specification, plan-rigor]
---

When plan B says 'blocked until plan A delivers X', retrieve plan A and verify the approved scope actually delivers X. Mismatches (e.g., A ships warnings, B expects structured API) create permanent blockers or force unexpected scope expansion into B.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
