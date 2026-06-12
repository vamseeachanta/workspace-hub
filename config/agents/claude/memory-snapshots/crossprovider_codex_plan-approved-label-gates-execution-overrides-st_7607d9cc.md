---
name: crossprovider codex plan-approved-label-gates-execution-overrides-st
description: Plan-approved label gates execution, overrides stale plan file state
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [governance, github-labels, plan-approval]
---

When an issue carries `status:plan-approved` GitHub label but the referenced plan file contains 'draft' status or unresolved review notes in its metadata, the live label is the execution gate. Proceed under label approval; document the metadata mismatch in closeout evidence rather than treating file state as blocking.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
