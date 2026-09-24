---
name: crossprovider codex numerical-solver-tests-must-verify-output-matche
description: Numerical solver tests must verify output matches input constraints, not just feasibility
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [numerical-testing, invariant-validation, constraint-solving, solver-correctness]
---

Catenary solver tests checked only `grounded_length > 0` (feasibility), missing that solved `top_tension` (≈532 kN) did not match input `pretension` (500 kN). Test passes while contract fails. Fix: assert output invariants (top_tension ≈ input pretension within tolerance) and impossible-input rejection (pretension < vertical line weight).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
