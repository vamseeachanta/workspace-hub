---
name: crossprovider codex approval-scope-assumptions-pattern-for-data-depe
description: Approval-scope assumptions pattern for data-dependent plans
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-design, data-handling, fail-closed, governance]
---

Plans involving uncertain sources (coefficients, fixtures, vendored standards) should explicitly list approval-scope assumptions that require user sign-off, then fail-closed at implementation if sources cannot be materialized — never invent or substitute placeholder data silently. This separates what needs user judgment (trade-offs, data source choices) from what implementation will handle.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
