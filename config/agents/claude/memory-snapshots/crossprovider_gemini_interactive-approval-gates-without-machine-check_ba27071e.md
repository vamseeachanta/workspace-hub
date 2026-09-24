---
name: crossprovider gemini interactive-approval-gates-without-machine-check
description: Interactive approval gates without machine-checkable evidence do not actually gate
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [gating, approval-workflows, governance]
---

WRK-1017 core problem: agents reached Stage 6 without Stage 5 evidence. Human approval must be captured in machine-verifiable format (YAML with required fields: `wrk_id`, `review_cycle_id`, `approval_decision`, `reviewed_at`, `reviewed_by`, `capture_method`). Free-text notes or ad-hoc YAML edits do not satisfy gate predicates.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
