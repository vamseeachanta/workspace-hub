---
name: crossprovider codex plan-status-gate-transitions-must-be-explicit-no
description: Plan status gate transitions must be explicit, not assumed
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [workflow-gates, status-labels, approval-process]
---

Plans that propose jumping from `status:pending` directly to `status:plan-approved` without stating explicit movement through `status:plan-review` violate the issue-planning workflow (Plan → Adversarial Review → `status:plan-review` → USER APPROVES → `status:plan-approved`). Approval readiness requires review artifacts to exist and all MAJOR findings to be resolved before user can apply final approval label.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
