---
name: crossprovider codex lifecycle-transition-gates-must-be-explicitly-en
description: Lifecycle transition gates must be explicitly encoded in plan text, not left as implied status changes
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [lifecycle-gates, plan-structure, change-control]
---

A plan saying 'status: draft' and 'status: plan-approved' blocks implementation' is insufficient. The gate from draft→plan-review must be explicitly stated: commit/push plan+artifacts, verify remote HEAD matches, post evidence comment with SHA/paths/verdicts, then apply status:plan-review. Without explicit gate text, transitions are ambiguous and reviewers miss required steps like pushing the plan to remote.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
