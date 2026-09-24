---
name: crossprovider codex frequency-dependent-eigenproblem-requires-explic
description: Frequency-dependent eigenproblem requires explicit convergence contract in TDD
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [frequency-dependent, eigenproblem, solver-domain, tdd-requirement]
---

Plans using iterative A(omega) methods (frequency-dependent added-mass in coupled eigenproblem) must define: interpolation domain and method, convergence tolerance and max iterations, mode tracking for repeated/crossing modes, handling of non-convergence and semidefinite restoring modes. Cannot lock single-point regression (e.g., A44 at 18.5 s) without self-consistent frequency at convergence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
