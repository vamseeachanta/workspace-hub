---
name: crossprovider hermes hydrodynamic-coupling-means-added-mass-matrices-
description: Hydrodynamic coupling means added-mass matrices aren't symmetric
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hydrodynamics, matrices, physics-insight]
---

Standard linear algebra assumes symmetric matrices, but hydrodynamic added-mass matrices show non-symmetric entries due to cross-coupling between DOFs (e.g., heave-pitch coupling). Symmetry tests must use loose tolerance (~1-2% error) or separate verification; expecting symmetry masks real physics.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
