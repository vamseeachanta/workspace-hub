---
name: crossprovider codex child-plans-must-re-state-lifecycle-gates-blocka
description: Child plans must re-state lifecycle gates; blockage inheritance is insufficient
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-gates, lifecycle-ownership, approval-workflow]
---

Plans that declare "blocked by #NNNN" but omit their own approval/review/legal/de-id criteria assume reviewers will track parent status. Child plans must explicitly state their own gate status (needs-plan, plan-approved, needs-review) independent of blockers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
