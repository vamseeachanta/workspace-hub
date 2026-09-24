---
name: crossprovider gemini openfoam-interfoam-multiphase-pressure-field-nam
description: OpenFOAM interFoam multiphase pressure field naming
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [openfoam, multiphase-flow, field-naming]
---

Multiphase simulations using OpenFOAM's `interFoam` solver expect the pressure field in `0/p_rgh`, not `0/p`. Writing pressure to the wrong field location causes solver initialization failure or convergence issues. Domain-specific gotcha worth checking in solver configuration.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
