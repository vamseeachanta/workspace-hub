---
name: crossprovider hermes pre-approved-queue-governance-gate-is-load-beari
description: Pre-approved queue governance gate is load-bearing
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [workflow-governance, execution-gate, policy-enforcement]
---

Workspace-hub policy forbids execution on pre-approved items (Issue → Plan → Review → Approval → status:plan-approved → Execute). Sampling showed all 4 plan-review items remain blocked; this gate prevents implementation of unresolved blockers.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
