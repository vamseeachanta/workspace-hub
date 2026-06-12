---
name: crossprovider hermes hydrodynamic-matrices-break-symmetry-due-to-coup
description: Hydrodynamic matrices break symmetry due to coupling
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hydrodynamics, matrix-properties, coupling, domain-knowledge]
---

Added mass and damping matrices in hydrodynamics have off-diagonal coupling terms between DOFs that violate the symmetry assumption. Naive M[i,j] == M[j,i] checks fail; either use loose relative tolerance or skip symmetry verification for coupled hydro systems. This is domain-specific and not a general matrix property.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
