---
name: crossprovider hermes adversarial-review-detects-plan-level-contradict
description: Adversarial review detects plan-level contradictions via test-naming
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [adversarial-review, plan-approval, testing, defect-class]
---

Internal contradictions in plans (e.g., test name says `test_planning_allowed_for_needs_plan` but spec says report-only for `status:needs-plan`) are hard-gate misses that charitable review misses. Adversarial reviewers must check TDD test names/descriptions against actual pseudocode/acceptance criteria.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
