---
name: crossprovider codex mixed-provenance-transformation-must-aggregate-c
description: Mixed-provenance transformation must aggregate conservatively
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-provenance, aggregation]
---

When interpolation or transformation combines solver-sourced and placeholder data, provenance must be conservatively aggregated: all-solver remains solver, any placeholder becomes placeholder, otherwise unknown. Copying only the first input's source silently upgrades mixed evidence to solver-level, creating false verdicts on fabricated coefficients.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
