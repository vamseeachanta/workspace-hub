---
name: crossprovider hermes source-identity-governance-requires-explicit-fai
description: Source-identity governance requires explicit fail-closed gates, not scoring alone
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [data-governance, privacy, plan-specification]
---

Plans treating completeness scores as implicit publication approval leak private/unsanitized sources. Data plans must explicitly define: source_doc_key derivation (opaque canonical ID, not raw paths), missing-source failure mode, score ≠ publication gate, required metadata (source_class, residency, sanitization state, review gate). Dependency references alone do not operationalize gates; plans must block execution until dependent issues reach approved/implemented state.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
