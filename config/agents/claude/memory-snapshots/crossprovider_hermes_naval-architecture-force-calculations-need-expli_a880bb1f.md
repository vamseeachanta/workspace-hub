---
name: crossprovider hermes naval-architecture-force-calculations-need-expli
description: Naval-architecture force calculations need explicit coordinate transforms when heading changes frame
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [naval-architecture, hydrodynamics, frame-transforms, physics-contract]
---

Reusing `X = F sin²(α)`, `Y = F sin(α) cos(α)` with heading-offset-adjusted inflow angle changes the physics frame (current-aligned vs ship-fixed) without transform. digitalmodel proj-a#598 MAJOR: must define local current frame, explicit local→ship rotation, and verify all tests use consistent frame. Deferring this creates silent component/sign mismatches.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
