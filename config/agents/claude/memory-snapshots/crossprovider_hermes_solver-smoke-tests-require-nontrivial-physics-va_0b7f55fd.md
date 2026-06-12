---
name: crossprovider hermes solver-smoke-tests-require-nontrivial-physics-va
description: Solver smoke tests require nontrivial physics validation, not just exit-code checks
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, fem-solver, portfolio-credibility]
---

CalculiX smoke test passing (returncode==0, .frd/.dat file existence) does not validate physical correctness. #2511 showed all-zero displacement/stress in 'successful' smoke, caused by missing mechanical loads and empty *CLOAD cards. For portfolio/job credibility, smoke gates must validate nonzero results and mesh convergence, not just file emission.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
