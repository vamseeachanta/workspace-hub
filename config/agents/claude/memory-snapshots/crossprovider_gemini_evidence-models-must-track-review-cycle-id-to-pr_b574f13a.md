---
name: crossprovider gemini evidence-models-must-track-review-cycle-id-to-pr
description: Evidence models must track review_cycle_id to prevent artifact mixing
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [gating, approval-workflows, evidence-model]
---

WRK-1017 gate design: `review_cycle_id` must match across all Stage 5 evidence artifacts (common-draft, plan-draft, browser-open, publish events). Mixed-cycle artifacts cause fail-closed gate violations. Without cycle tracking, retry loops or manual review re-runs create orphaned approval evidence.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
