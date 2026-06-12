---
name: crossprovider codex fallback-candidate-evaluation-for-singular-linea
description: Fallback candidate evaluation for singular linear systems
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [numerical-stability, mesh-simplification, fallback-pattern]
---

When solving a linear system Q*v = b fails due to singularity (det near zero), evaluate the error metric at multiple candidate points (e.g., endpoints, midpoint) and select the minimum-cost position. More robust than returning a default or propagating the error.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
