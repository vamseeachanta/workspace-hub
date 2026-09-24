---
name: crossprovider gemini policy-scenario-truth-tables-are-approval-gates
description: Policy scenario truth tables are approval gates
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [governance, policy, review]
---

Governance policies need explicit edge-case scenario matrices covering non-obvious cases (auth_failed, same-timestamp ties, unreachable branches, terminal event known then branch unreachable) to be approval-ready. Approval should be blocked until all rows are defined.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
