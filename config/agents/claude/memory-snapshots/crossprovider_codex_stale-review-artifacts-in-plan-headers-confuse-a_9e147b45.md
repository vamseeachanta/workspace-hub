---
name: crossprovider codex stale-review-artifacts-in-plan-headers-confuse-a
description: Stale review artifacts in plan headers confuse approval gates
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, governance, approval-gate]
---

When a plan undergoes multiple adversarial review rounds (r1, r2, r3…), the plan header and `Adversarial Review Summary` must be updated after each round to show the current verdict and review result. Leaving prior-round MAJOR/FAILED verdicts in place tricks reviewers and makes it impossible to distinguish stale wording from actual approval-readiness.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
