---
name: crossprovider hermes status-labels-actively-gate-engineering-workflow
description: Status labels actively gate engineering workflows
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [labels, workflow-gates, github-api]
---

Labels like `status:needs-plan` and `status:plan-review` are not organizational metadata but load-bearing workflow gates; if they don't exist, workflows adapt or create them. Labels enforce state machine transitions in issue-planning mode.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
