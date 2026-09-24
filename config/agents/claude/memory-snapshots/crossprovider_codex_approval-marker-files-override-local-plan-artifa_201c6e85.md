---
name: crossprovider codex approval-marker-files-override-local-plan-artifa
description: Approval marker files override local plan artifact status
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [approval-gates, git-workflow, workspace-hub]
---

When live GitHub labels show `status:plan-approved` but local plan files say 'draft', trust the approval marker at `.planning/plan-approved/<issue-id>.md`. This indicates the gate has passed even if the plan artifact wasn't locally updated.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
