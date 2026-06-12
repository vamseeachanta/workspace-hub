---
name: crossprovider hermes plan-approved-labels-decay-without-active-hygien
description: Plan-approved labels decay without active hygiene checks
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [github-issue-gates, label-hygiene, execution-readiness]
---

Issues labeled `status:plan-approved` can have stale or missing plan files; dual labeling (`status:plan-review` + `status:plan-approved`) signals decay. Hygiene audit before execution is required: verify plan file exists, approval markers are valid, and labels are consistent.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
