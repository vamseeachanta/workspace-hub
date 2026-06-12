---
name: crossprovider hermes live-github-label-drift-vs-local-state-must-be-r
description: Live GitHub label drift vs local state must be reconciled before declaring clean
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [github-labels, state-reconciliation]
---

Issues can have mismatched GitHub labels (e.g., `status:plan-approved` remotely while plan says `plan-review`). These divergences must be detected and reconciled via `gh issue view` before declaring plan state clean.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
