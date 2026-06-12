---
name: crossprovider hermes discretization-boundary-state-errors-hide-in-str
description: Discretization boundary-state errors hide in structure-only tests
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [simulation, testing, discretization, physics]
---

When duration/dt is non-integer, simulation timestep bugs let tests pass if they only verify endpoint existence. Must separately verify endpoint state is computed with correct remainder logic, not bulk-advanced from a full step.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
