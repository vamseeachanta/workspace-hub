---
name: crossprovider hermes plan-only-mode-with-mandatory-user-approval-stop
description: Plan-only mode with mandatory user-approval stop
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [planning-workflow, approval-gates, user-in-loop]
---

Overnight planning runs must stop at `status:plan-review` and post 'ready for approval' comment. Only move to `status:plan-approved` and implementation after explicit user approval. Never self-approve.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
