---
name: crossprovider gemini github-workflow-gate-labels-drift-from-plan-arti
description: GitHub workflow-gate labels drift from plan artifact state
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [governance, github-labels, workflow-gates, issue-validation]
---

When issues are prepared via handoff generation, workflow-gate labels (e.g., `status:plan-approved`) are often applied before the canonical plan artifact is created. #2442 and #2443 both carried approval labels without plan files at review time. This label-state vs artifact-state divergence is expected in handoff workflows. Do not treat pre-applied labels as approval evidence until the plan artifact exists.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
