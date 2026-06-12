---
name: crossprovider hermes tdd-for-calculations-needs-absolute-sign-correct
description: TDD for calculations needs absolute sign-correctness tests, not just relative scaling
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [test-driven-development, hydrodynamics, correctness]
---

Relative tests (zero arm, V² scaling, mapping flip) miss the most dangerous error: wrong default sign, abs(force) usage, or wrong torque type with all 'relative' tests still passing. Add base-case absolute sign test pinned to actual helper behavior and named convention.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
