---
name: crossprovider gemini log-gate-action-names-vary-by-workflow-phase
description: Log gate action names vary by workflow phase
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [agent-infrastructure, gate-contract, logging]
---

claim phase requires: routing action (work_wrapper_complete or work_queue_skill) + plan action (plan_draft_complete or plan_wrapper_complete). close phase adds: execute action (execute_wrapper_complete or tdd_eval) + cross-review action (review_wrapper_complete or agent_cross_review). Log schema: {timestamp, wrk_id, stage, action, signal, provider}.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
