---
name: crossprovider gemini user-reviews-plan-html-before-multi-agent-review
description: User reviews plan HTML before multi-agent review
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [governance, process-optimization, review-gates, work-queue]
---

Plan HTML artifacts must be reviewed by user BEFORE multi-agent review cycle starts, not after. Prevents wasteful re-review rounds when user feedback requires plan revisions. Enforced in WRK-624 canonical lifecycle via `plan_html_reviewed_draft` gate.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
