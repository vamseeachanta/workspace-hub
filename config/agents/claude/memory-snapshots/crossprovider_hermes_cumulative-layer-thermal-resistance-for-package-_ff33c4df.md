---
name: crossprovider hermes cumulative-layer-thermal-resistance-for-package-
description: Cumulative layer thermal resistance for package FEM node temperatures
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [fem, thermal-analysis, semiconductor-packaging]
---

In semiconductor package thermal/thermo-mechanical FEM, node temperatures must be computed using cumulative per-layer thermal resistance (ΔT = power × thickness / (k × area)), accumulating layer-by-layer, then interpolating within each layer before emitting per-node boundary conditions. Linear total-thickness scaling produces incorrect profiles. Validated in #2511 with CalculiX smoke test.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
