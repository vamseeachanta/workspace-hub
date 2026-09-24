---
name: crossprovider codex plan-approval-gates-must-synchronize-between-pla
description: Plan approval gates must synchronize between plan text and GitHub labels
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [gate-synchronization, plan-approval, process-risk, github-labels]
---

A plan claiming `plan-approved` while the issue shows `status:plan-review` creates authorization ambiguity that blocks implementation. This gate is enforced across multiple review stages (adversarial, standards, spec). Both the plan document and GitHub issue labels must be updated together for authorization to be unambiguous.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
