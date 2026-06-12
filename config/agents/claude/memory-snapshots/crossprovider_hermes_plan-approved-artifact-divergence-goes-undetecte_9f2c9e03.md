---
name: crossprovider hermes plan-approved-artifact-divergence-goes-undetecte
description: Plan-approved artifact divergence goes undetected
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [gates, plan-alignment, review]
---

Implementations silently deviate from approved plans (missing polar overlays, unremoved resultants) while tests pass. Need explicit checklist validation: read plan body, verify each recommended step is present in code, not inferred.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
