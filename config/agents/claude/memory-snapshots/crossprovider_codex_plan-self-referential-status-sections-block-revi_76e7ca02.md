---
name: crossprovider codex plan-self-referential-status-sections-block-revi
description: Plan self-referential status sections block review gate transition
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [planning, review-gates, workflow]
---

Plans containing text like 'this remains failed/draft until fresh review exists' self-block moving to status:plan-review status, even if those sections are historical. Only update review summary sections after a fresh review passes; treat stale summaries as pre-review state until explicitly refreshed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
