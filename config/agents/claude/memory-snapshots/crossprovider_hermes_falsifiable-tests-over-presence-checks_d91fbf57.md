---
name: crossprovider hermes falsifiable-tests-over-presence-checks
description: Falsifiable tests over presence checks
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [test-design, falsifiability, test-quality]
---

Move away from presence-oriented tests ("X exists") toward negative/mutation tests that verify behavior when X is absent, modified, or in edge states. This makes test suites more resilient to accidental failures and better catches regressions.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
