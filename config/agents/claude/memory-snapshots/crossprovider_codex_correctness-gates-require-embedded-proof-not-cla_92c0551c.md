---
name: crossprovider codex correctness-gates-require-embedded-proof-not-cla
description: Correctness gates require embedded proof, not claims
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [plan-review, verification, tdd]
---

Plans cannot say 'this gate passes' without an embedded red/green command or artifact in the plan. Statements like 'flake8 reduced or clean with residual blockers tracked' are insufficient if the issue requires the gate to exit 0; the exact command and its pre/post output must be included.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
