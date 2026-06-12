---
name: crossprovider hermes tdd-red-implementation-validation-is-fragile-acr
description: TDD (RED → implementation → validation) is fragile across context boundaries
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [test-driven-development, context-management, red-first]
---

Sessions show repeated intent to write RED tests first, then GREEN, but context compressions interrupt the cycle. Test state must either: (a) complete in single session, or (b) explicitly preserve test fixture/expected-failure state in .planning/ for next session to resume from. Mixed partial progress causes tool-call waste.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
