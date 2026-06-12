---
name: crossprovider hermes workspace-hub-hard-stop-workflow-is-unyielding
description: Workspace-hub hard-stop workflow is unyielding
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [policy, workflow, approval-gate]
---

Workspace-hub enforces Issue → Plan → Adversarial review → User approves → status:plan-approved → Implement. Agents cannot bypass this policy even when instructed to execute work; maximum safe action for pre-approval issues is planning/review/hardening only, not implementation or merge.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
