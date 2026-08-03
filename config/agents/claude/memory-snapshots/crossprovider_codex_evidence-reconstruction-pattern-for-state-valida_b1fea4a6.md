---
name: crossprovider codex evidence-reconstruction-pattern-for-state-valida
description: Evidence reconstruction pattern for state validation
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [validation, security, state-management, trust-model]
---

External serialized documents (manifests, config serializations) are untrusted claims, not authority. Validation should reconstruct the expected state from trusted sources (schema, trusted configuration) plus live descriptor reads, then compare against the claimed state. This prevents document-based authority bypasses and in-place mutations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
