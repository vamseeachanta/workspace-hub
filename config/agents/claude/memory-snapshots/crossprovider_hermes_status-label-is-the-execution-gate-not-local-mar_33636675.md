---
name: crossprovider hermes status-label-is-the-execution-gate-not-local-mar
description: Status label is the execution gate, not local markers
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [github-labels, approval-gates, execution-signal]
---

`status:plan-approved` GitHub label (not `.planning/plan-approved/` marker files) unblocks implementation. Label-is-the-gate convention: if label exists, local marker missing is acceptable. This decouples approval from filesystem state.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
