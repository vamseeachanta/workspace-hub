---
name: crossprovider hermes plan-approved-is-a-hard-workflow-gate
description: Plan-approved is a hard workflow gate
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [governance, workflow, gate]
---

workspace-hub policy enforces: Issue → Plan → Adversarial review → User approves plan → status:plan-approved label → Only then execute. Multiple sessions attempted to bypass or auto-approve; all hit a hard stop. The gate is non-negotiable.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
