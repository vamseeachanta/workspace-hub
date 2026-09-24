---
name: crossprovider codex approval-drift-requires-multi-factor-verificatio
description: Approval drift requires multi-factor verification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [approval-gates, workflow-safety, label-drift]
---

A GitHub `status:plan-approved` label alone does not indicate execution-ready state. The workspace's hard gate requires BOTH the label AND a durable local approval marker file (`.planning/plan-approved/NNNN.md`) before work is safe to execute. Queues that rely on label state alone mask blocked or rotten approvals.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
