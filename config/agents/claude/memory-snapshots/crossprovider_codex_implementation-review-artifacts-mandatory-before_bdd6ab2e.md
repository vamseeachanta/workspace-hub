---
name: crossprovider codex implementation-review-artifacts-mandatory-before
description: Implementation review artifacts mandatory before issue closeout
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [governance, review-artifacts, closeout]
---

Before closing an issue, `scripts/review/results/` must contain `*implementation-NN*` artifacts (distinct from plan-review). Flow: plan-approved → implementation → cross-review artifacts → issue comment → close. Absence of implementation-review artifacts is a MAJOR gate violation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
