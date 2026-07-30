---
name: crossprovider codex plan-gated-validation-requires-explicit-rejectio
description: Plan-gated validation requires explicit rejection tests for each rule criterion
metadata:
  type: reference
  source: codex
  bridged: 2026-07-06
  tags: [tdd, plan-gating, validation, test-coverage]
---

When a plan specifies validation rules, TDD must explicitly test rejection of each criterion class, not indirect coverage through acceptance tests. For example: rejected direct factor with secondary source, rejected ranged/non-representative factor—each as its own test case, not bundled with loader acceptance tests.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
