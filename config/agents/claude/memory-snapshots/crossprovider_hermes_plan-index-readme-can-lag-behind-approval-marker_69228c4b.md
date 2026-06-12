---
name: crossprovider hermes plan-index-readme-can-lag-behind-approval-marker
description: Plan-index README can lag behind approval markers and handoff logs
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [documentation-drift, plan-state, approval-precedence]
---

Docs/plans/README.md is a snapshot and may understate approved/completed plan status relative to local approval markers and session handoff evidence. When resolving whether a plan is plan-review vs plan-approved, apply latest-status-precedence: check local markers first, then handoff logs, then GitHub labels. README is a trailing index, not the source of truth.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
