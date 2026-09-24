---
name: crossprovider codex work-queue-integrity-gates-require-plan-approval
description: Work queue integrity gates require plan-approval and state consistency
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [governance, queue-integrity, verification]
---

Violations include items in 'working' but plan_approved:false, state.yaml drift from actual WRKs, duplicate IDs. Automated queue checks needed: ID uniqueness, status/approval consistency, state counter accuracy vs actual inventory.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
