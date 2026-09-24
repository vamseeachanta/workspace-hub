---
name: crossprovider codex approval-must-record-exact-commit-blob-durably-b
description: Approval must record exact commit/blob durably before Task 0
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [approval-gating, plan-approved, git-traceability]
---

Record the precise commit hash of the approved plan before executing Task 0 (dependency verification). Enables audit trail, prevents approval-drift, and allows rollback if dependencies change. Must be committed and pushed to a tracked branch, not just noted locally.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
