---
name: crossprovider codex field-level-provenance-lost-when-design-to-plan-
description: Field-level provenance lost when design-to-plan reduces multi-source assemblies to single chains
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [provenance, lineage, specification-completeness]
---

Design promises 'retain source-field lineage'; plan reduces to source_sha256 → normalized_sha256 single chain. Multi-source assemblies (components + rig data + environment + criteria + synthetic assumptions) require tracking per-field sources, transformation versions, and completeness. Single-chain lineage loses this traceability.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
