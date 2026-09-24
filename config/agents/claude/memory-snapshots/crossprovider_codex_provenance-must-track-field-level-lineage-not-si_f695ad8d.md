---
name: crossprovider codex provenance-must-track-field-level-lineage-not-si
description: Provenance must track field-level lineage, not singular chain
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [provenance, field-lineage, data-reproducibility, schema-design]
---

Configurations assembled from multiple sources (components, rig data, environment, synthetic assumptions) require per-field source tracking. A singular source_sha256 → normalized_sha256 chain collapses necessary traceability. Spec must mandate field-level source locator, transformation version, and per-field source hash set for audit.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
