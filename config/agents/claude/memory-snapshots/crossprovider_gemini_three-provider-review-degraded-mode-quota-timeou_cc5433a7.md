---
name: crossprovider gemini three-provider-review-degraded-mode-quota-timeou
description: Three-provider review degraded mode: quota/timeout failure → eligibility, not automatic bypass
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [multi-provider-review, workflow-orchestration, approval-gates]
---

When one explicit provider fails (quota, auth, timeout >60s), degraded mode becomes eligible but still requires explicit user approval in machine-checkable evidence (not inferred). Mixed-cycle artifacts (different review_cycle_id) fail closed. Approval scope must be recorded.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
