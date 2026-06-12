---
name: crossprovider gemini single-logging-abstraction-prevents-schema-drift
description: Single logging abstraction prevents schema drift
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [infrastructure, logging, architecture]
---

When extending logging/gate infrastructure to new providers, route through existing abstractions (log-gate-event.sh, workflow-guards.sh) rather than creating parallel logging paths. A single canonical schema with one writer prevents provider-specific divergence and simplifies verification.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
