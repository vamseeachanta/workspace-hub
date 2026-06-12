---
name: crossprovider hermes issue-dispatch-dual-gate-github-label-plus-local
description: Issue dispatch dual-gate: GitHub label plus local marker both required
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [workflow, github-issue-management, dispatch-gates]
---

Issues with GitHub `status:plan-approved` label still block if committed `.planning/plan-approved/<issue>.md` marker is missing. Dispatcher requires BOTH gates; missing either one halts implementation even if plan exists and label is live. Recurring pattern across #2490, #2566–#2568: label present, marker absent → blocked.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
