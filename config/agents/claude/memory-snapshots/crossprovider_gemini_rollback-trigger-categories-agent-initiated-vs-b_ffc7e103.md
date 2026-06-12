---
name: crossprovider gemini rollback-trigger-categories-agent-initiated-vs-b
description: Rollback trigger categories: agent-initiated vs bypass-initiated
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [rollback-policy, governance, enforcement-gates]
---

Agent-initiated rollback (test failure → auto-revert per TRUST-ARCHITECTURE) differs from bypass-initiated (gate skipped → detected later → decide disposition). Bypass-initiated requires separate policy matrix: auto-revert / guided revert / log-only advisory.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
