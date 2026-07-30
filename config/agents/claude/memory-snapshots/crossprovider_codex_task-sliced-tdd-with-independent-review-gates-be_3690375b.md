---
name: crossprovider codex task-sliced-tdd-with-independent-review-gates-be
description: Task-sliced TDD with independent review gates between slices
metadata:
  type: reference
  source: codex
  bridged: 2026-07-18
  tags: [workflow, tdd, code-review, large-features]
---

Break large features into 3–5 discrete task slices. TDD each independently with focused tests and path-scoped commits, then require independent adversarial review before advancing to the next slice. This pattern caught schema edge cases, contract gaps, and traceability defects that would have propagated downstream into data and reporting layers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
