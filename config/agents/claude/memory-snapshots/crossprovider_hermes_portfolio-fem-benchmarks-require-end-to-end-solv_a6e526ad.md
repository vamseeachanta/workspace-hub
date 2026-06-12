---
name: crossprovider hermes portfolio-fem-benchmarks-require-end-to-end-solv
description: Portfolio FEM benchmarks require end-to-end solver validation, not analytical proxies
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [portfolio-credibility, fem-validation]
---

For job/career artifacts, FEM benchmarks claiming 'package thermal/thermo-mechanical analysis' must include: actual solver execution, convergence diagnostics (.cvg/.sta parsing), nodewise result extraction, and sensitivity to input parameters (power, CTE, geometry). Analytical approximations are acceptable only if explicitly labeled as sanity checks, not validation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
