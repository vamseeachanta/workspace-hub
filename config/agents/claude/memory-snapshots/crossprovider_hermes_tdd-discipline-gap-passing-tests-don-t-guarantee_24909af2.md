---
name: crossprovider hermes tdd-discipline-gap-passing-tests-don-t-guarantee
description: TDD discipline gap: passing tests don't guarantee spec compliance without fail-first validation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [tdd-discipline, test-spec-alignment, acceptance-criteria, test-driven-development]
---

When implementing TDD, tests passing doesn't mean acceptance criteria are met if tests never failed against spec first. Weak tests that don't validate against the plan's requirements (e.g., tests expect resultants but plan explicitly forbids them) indicate the test-first loop was skipped. Validate tests explicitly against plan acceptance gates before considering implementation complete.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
