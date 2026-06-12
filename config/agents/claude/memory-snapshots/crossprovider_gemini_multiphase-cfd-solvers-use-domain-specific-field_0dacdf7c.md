---
name: crossprovider gemini multiphase-cfd-solvers-use-domain-specific-field
description: Multiphase CFD solvers use domain-specific field names in templates
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [cfd-solvers, template-design, domain-specificity]
---

OpenFOAM multiphase solvers (e.g., `interFoam`) use `p_rgh` (relative hydrostatic pressure) not generic `p`. Field names are solver-specific and must live in solver templates/constants, not in generic pressure-field writers. Validate against actual solver documentation for each domain.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
