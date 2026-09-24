---
name: crossprovider codex status-labels-can-drift-from-local-plan-state
description: Status labels can drift from local plan state
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [label-drift, approval-state, audit-pattern]
---

GitHub issue labels (e.g., `status:plan-review`, `status:plan-approved`) may lag behind or contradict the actual state recorded in local plan files and approval markers under `docs/plans/`. GitHub labels are the queue authority for live triage; local artifacts are supporting evidence. Reconciliation audits must cross-check both.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
