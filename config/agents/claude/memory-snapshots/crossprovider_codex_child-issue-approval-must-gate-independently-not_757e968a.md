---
name: crossprovider codex child-issue-approval-must-gate-independently-not
description: Child issue approval must gate independently, not cascade from parent
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [workflow-gates, issue-planning, approval-boundaries]
---

Plans that require parent approval (e.g., #264) to implicitly authorize execution of child issues (#265–#269) violate issue-planning workflow. Each child must receive its own plan, adversarial review, and user approval at `status:plan-approved` before execution. Parent approval should authorize planning/orchestration only, not child implementation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
