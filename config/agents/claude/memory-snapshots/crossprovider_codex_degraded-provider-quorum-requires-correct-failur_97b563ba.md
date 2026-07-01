---
name: crossprovider codex degraded-provider-quorum-requires-correct-failur
description: Degraded provider quorum requires correct failure classification
metadata:
  type: reference
  source: codex
  bridged: 2026-06-30
  tags: [approval-gates, process, scope-boundaries]
---

Approval gates permit degraded quorum (e.g., T3→T2) only for provider quota outages, not local auth/config failures. Allowing downgrade for auth failures bypasses the multi-provider review requirement indefinitely—require explicit user escalation or restoration.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
