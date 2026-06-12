---
name: crossprovider hermes placeholder-code-passes-unit-tests-but-fails-acc
description: Placeholder code passes unit tests but fails acceptance
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [tdd, placeholder-implementation, acceptance-readiness]
---

Code with placeholder functions (sin() math, fake gates without real data, removed implementations causing browser errors) passes isolated unit tests but fails acceptance. TDD-first (write failing test before code) requires explicit test infrastructure for placeholder-to-real transitions.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
