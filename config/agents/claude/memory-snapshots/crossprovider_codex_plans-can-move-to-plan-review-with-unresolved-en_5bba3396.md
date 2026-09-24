---
name: crossprovider codex plans-can-move-to-plan-review-with-unresolved-en
description: Plans can move to plan-review with unresolved engineering inputs if fail-closed
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, fail-closed-gates, owner-decisions]
---

A plan with missing sources (e.g., OCIMF coefficients, vendor data) can move to `status:plan-review` if the missing sources are explicit fail-closed gates and owner-visible approval decisions, not hidden in implementation discretion. The plan must make clear the approval request is asking the owner to resolve/accept the decisions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
