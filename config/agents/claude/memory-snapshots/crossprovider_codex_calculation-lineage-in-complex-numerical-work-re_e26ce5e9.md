---
name: crossprovider codex calculation-lineage-in-complex-numerical-work-re
description: Calculation lineage in complex numerical work requires full specification
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [numerical-methods, reproducibility, documentation]
---

Iterative and frequency-dependent problems (eigenvalue, coupled dynamics) produce 'exact' values that are underdetermined without documented interpolation rules, convergence criteria, mode tracking, repeated-root handling, and non-convergence policy. Derived quantities like '20.946 s period' are meaningless without the A44(T) iteration rule and convergence target.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
