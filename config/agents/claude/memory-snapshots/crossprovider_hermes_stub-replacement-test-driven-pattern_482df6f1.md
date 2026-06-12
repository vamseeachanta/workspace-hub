---
name: crossprovider hermes stub-replacement-test-driven-pattern
description: Stub-replacement test-driven pattern
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [test-driven, placeholders, source-replacement, regression-testing]
---

When replacing placeholder implementations (trigonometry stubs, hardcoded constants) with real data adapters, write failing tests first for the new adapter behavior. Prevents silent regressions where placeholder-to-real transitions hide calculation errors.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
