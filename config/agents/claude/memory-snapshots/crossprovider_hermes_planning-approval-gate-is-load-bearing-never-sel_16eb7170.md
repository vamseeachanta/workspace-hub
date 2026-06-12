---
name: crossprovider hermes planning-approval-gate-is-load-bearing-never-sel
description: Planning approval gate is load-bearing; never self-label status:plan-approved
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [planning-workflow, approval-gates, multi-agent-coordination]
---

`status:plan-approved` is a strict user-in-loop gate enforced by workspace-hub planning workflow. Agent must stop at `status:plan-review`, post 'ready for approval' comment, and wait for explicit user label. Self-labeling or assuming pre-existing label without fresh user comment is a workflow violation; user approval must remain explicit each session.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
