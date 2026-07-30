---
name: crossprovider codex contract-status-fields-are-gates-not-passive-met
description: Contract status fields are gates, not passive metadata
metadata:
  type: reference
  source: codex
  bridged: 2026-07-20
  tags: [architecture, state-management, contracts]
---

Stateful fields in contract/manifest documents (e.g., owner_decision.status, reuse_allowed) are prerequisites and gates, not just documentation. Dependent work must explicitly check these before assuming approval. Document status fields as mandatory prerequisites in execution plans.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
