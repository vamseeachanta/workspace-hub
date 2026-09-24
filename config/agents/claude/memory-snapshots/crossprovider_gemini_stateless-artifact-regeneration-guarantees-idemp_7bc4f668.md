---
name: crossprovider gemini stateless-artifact-regeneration-guarantees-idemp
description: Stateless artifact regeneration guarantees idempotency over mutation
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [artifact-generation, idempotency, design-pattern]
---

Regenerating lifecycle HTML entirely from evidence files each invocation (no HTML parsing/mutation) eliminates fragility and guarantees idempotent output. Prefer rebuild-from-source over stateful mutation patterns for long-lived artifacts.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
