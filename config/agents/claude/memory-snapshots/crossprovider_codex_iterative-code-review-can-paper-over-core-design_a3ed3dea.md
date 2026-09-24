---
name: crossprovider codex iterative-code-review-can-paper-over-core-design
description: Iterative code review can paper over core design failures
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [code-review, testing, semantic-vs-syntactic]
---

Syntactic consumption (checking a dependency exists) is not the same as semantic consumption (reading and flowing its signals). A fix that only nominally checks enums, makes requirements optional with fallback, or presence-checks but ignores dependency semantics will pass code review but fail acceptance. Catch this by testing end-to-end output against the plan's actual acceptance criteria, not just the implementation's internal tests.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
