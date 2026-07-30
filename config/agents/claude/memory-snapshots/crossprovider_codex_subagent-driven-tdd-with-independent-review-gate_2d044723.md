---
name: crossprovider codex subagent-driven-tdd-with-independent-review-gate
description: Subagent-driven TDD with independent review gates between slices prevents cascading defects
metadata:
  type: reference
  source: codex
  bridged: 2026-07-18
  tags: [workflow, tdd, review-gates, multi-agent]
---

Each implementation slice (schema, data, reconciliation) gets its own adversarial review gate before advancing. This pattern caught forward-compatibility blockers and fail-open edge cases early that would have compounded in later slices. Independent review between slices costs more upfront but prevents rework and architecture debt.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
