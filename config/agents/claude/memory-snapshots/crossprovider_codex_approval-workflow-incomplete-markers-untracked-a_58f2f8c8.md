---
name: crossprovider codex approval-workflow-incomplete-markers-untracked-a
description: Approval workflow incomplete: markers untracked and artifact inventory unchecked
metadata:
  type: reference
  source: codex
  bridged: 2026-06-21
  tags: [approval-workflow, artifact-tracking, delivery-parity]
---

Approval markers (`.planning/plan-approved/748.md`) exist locally untracked; final patch doesn't track all named deliverables from approved plan artifact map; no verification that `git diff --name-status` matches approval artifact list. Approval gates must verify inventory before closure.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
