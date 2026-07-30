---
name: crossprovider codex reducing-multi-source-provenance-to-a-single-cha
description: Reducing multi-source provenance to a single chain loses field-level auditability
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [auditability, provenance, design-spec]
---

When lineage from configuration, rig data, environment, and synthetic assumptions is collapsed into one source_sha256→normalized_sha256 chain, field-level transformation tracking vanishes. "Provenance-safe SSOT" requires per-field source identifiers, transformation versions, and ordered source-hash sets.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
