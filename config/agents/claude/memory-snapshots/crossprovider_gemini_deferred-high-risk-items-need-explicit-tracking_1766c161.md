---
name: crossprovider gemini deferred-high-risk-items-need-explicit-tracking
description: Deferred high-risk items need explicit tracking
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [architecture, risk-management]
---

When deferring risky refactors (e.g., `.claude/agent-library/` rename), mark explicitly as 'HIGH RISK—deferred to WRK-XYZ'. Prevents accidental re-inclusion in adjacent cleanup and documents risk tradeoff.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
