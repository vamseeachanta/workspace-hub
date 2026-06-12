---
name: crossprovider hermes rotational-dof-unit-mismatch-in-hydrodynamic-com
description: Rotational DOF unit mismatch in hydrodynamic comparisons
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [orcawave, rao-extraction, hydrodynamics, unit-convention, bug-pattern]
---

When comparing extracted RAO data against benchmark YAML: translational DOFs (Surge/Sway/Heave) match to <0.03% error, but rotational DOFs (Roll/Pitch/Yaw) show ~98% error. Indicates radians vs degrees mismatch between tools. Check unit handling when comparing CFD output across solvers.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
