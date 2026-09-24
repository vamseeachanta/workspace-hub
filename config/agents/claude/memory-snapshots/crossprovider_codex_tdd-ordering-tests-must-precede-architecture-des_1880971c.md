---
name: crossprovider codex tdd-ordering-tests-must-precede-architecture-des
description: TDD ordering: tests must precede architecture description
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tdd, test-first, plan-discipline]
---

Plans that describe implementation, overrides, or architecture rules before listing test cases violate test-first discipline. Each behavior change must be observable RED → GREEN → refactor cycle, not architecture-then-tests. Test order matters for reproducibility.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
