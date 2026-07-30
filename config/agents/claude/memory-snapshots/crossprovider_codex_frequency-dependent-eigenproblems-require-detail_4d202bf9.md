---
name: crossprovider codex frequency-dependent-eigenproblems-require-detail
description: Frequency-dependent eigenproblems require detailed acceptance criteria
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [numerical-methods, acceptance-criteria, eigenvalue-problems, specifications]
---

Plans that require frequency-dependent added-mass correction + iterative eigenvalue solve MUST specify: interpolation domain, convergence tolerance, mode tracking/identification, extrapolation policy, repeated/crossing-mode handling, and self-consistent expected result. A single-point regression is insufficient; add tests for zero/semidefinite cases and mode tracking.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
