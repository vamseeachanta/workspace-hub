---
name: crossprovider codex coordination-rows-drift-when-plan-deferrals-aren
description: Coordination rows drift when plan deferrals aren't propagated
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, cross-artifact-consistency, coordination]
---

After plan-stage review surfaces deferrals (format exclusions, metric gates), update the coordinating ledger/index row to match. Otherwise readers inherit stale success criteria and misaligned yield expectations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
