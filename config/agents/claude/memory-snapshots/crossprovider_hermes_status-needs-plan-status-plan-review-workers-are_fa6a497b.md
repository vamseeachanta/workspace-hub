---
name: crossprovider hermes status-needs-plan-status-plan-review-workers-are
description: Status:needs-plan / status:plan-review workers are report-only, never execute
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cron-orchestration, hard-gate, state-machine, workspace-hub]
---

For cron orchestration MVP: only `status:plan-approved` + local `.planning/plan-approved/<issue>.md` marker allows provider execution. Earlier statuses must emit reports/evidence/comments without running tools. This boundary prevents accidental task execution before user approval.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
