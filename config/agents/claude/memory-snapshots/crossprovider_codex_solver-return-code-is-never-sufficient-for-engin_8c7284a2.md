---
name: crossprovider codex solver-return-code-is-never-sufficient-for-engin
description: Solver return code is never sufficient for engineering acceptance
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [engineering-gates, solver-validation, aqwa, orcawave]
---

Zero exit code from solvers like AQWA/OrcaWave does not constitute acceptance. Closure criteria include independent solver agreement on hydrostatics, matrix credibility (no negative added-mass diagonals), and physical plausibility of results (e.g., roll response period). A passing exit code must be paired with independent verification before accepting results.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
