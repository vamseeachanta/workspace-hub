---
name: crossprovider hermes live-github-verification-required-for-approval-s
description: Live GitHub verification required for approval-state audits
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [governance, approval-workflow, git-sync]
---

Approval/portfolio audits must fetch and verify live GitHub issue labels/status before acting; stale handoff assumptions are insufficient. This prevents silent governance drift where local decisions don't match upstream label/status state.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
