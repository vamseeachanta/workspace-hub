---
name: crossprovider codex approval-marker-drift-local-planning-plan-approv
description: Approval marker drift: local .planning/plan-approved file can be stale if plan body changes post-approval
metadata:
  type: reference
  source: codex
  bridged: 2026-07-08
  tags: [governance, approval-gates, state-consistency]
---

A plan approved at commit A retains its approval marker even if the plan body is revised at commit B. Approval-state checks must verify that current plan content matches what was actually reviewed and approved; local markers alone are insufficient. Observed in worldenergydata where approval marker existed but approval-blocking sentence remained in current plan.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
