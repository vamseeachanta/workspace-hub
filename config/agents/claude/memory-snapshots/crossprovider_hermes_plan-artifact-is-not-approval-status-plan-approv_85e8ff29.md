---
name: crossprovider hermes plan-artifact-is-not-approval-status-plan-approv
description: Plan artifact is not approval; status:plan-approved label is the gate
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [approval-workflow, github-labels, gating]
---

A plan document (status:plan-review) is discussion, not consent to implement. Implementation requires explicit user approval (GitHub comment/chat) AND status label change to status:plan-approved. This gate is load-bearing; skipping it results in unauthorized scope execution.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
