---
name: crossprovider hermes umbrella-issue-splits-require-plan-scope-rewrite
description: Umbrella issue splits require plan scope rewrite
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [issue-decomposition, scope-alignment, plan-staleness]
---

When umbrella issues decompose into child issues (e.g., #2216 splits to #2225, #2226, #2227), the parent plan becomes stale. Rewrite plan against child scope, not parent assumptions. Approval-ready plans must match current issue decomposition, not archived state.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
