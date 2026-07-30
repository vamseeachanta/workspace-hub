---
name: crossprovider codex task-gated-tdd-with-independent-review-between-s
description: Task-gated TDD with independent review between slices prevents defect accumulation
metadata:
  type: reference
  source: codex
  bridged: 2026-07-18
  tags: [testing-tdd, review-gates, regression-tests]
---

Implementation uses strict gates where each task is reviewed independently before advancing to the next. Schema/contract RED-GREEN implementation with regression tests catching defects early (foreign-key failures, type mismatches) that wouldn't surface in single-pass reviews. Multi-round adversarial review catches progressively deeper semantic issues.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
