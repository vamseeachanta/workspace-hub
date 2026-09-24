---
name: crossprovider gemini reuse-existing-infrastructure-over-new-abstracti
description: Reuse existing infrastructure over new abstractions for same concern
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [architecture, DRY-principle, single-source-of-truth]
---

When logging already works via workflow-guards.sh + log_gate_event_if_available(), ensure all providers call that shared path rather than creating parallel log-helper abstractions. Single source of truth eliminates duplicate implementations and reduces maintenance burden.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
