---
name: crossprovider codex manifest-metadata-must-declare-units-and-source-
description: Manifest metadata must declare units and source paths
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [manifest, metadata, catalog]
---

Catalog manifest validation must check schema versions, required output set, declared columns, and units. Output metadata must include field-level units, not just digest and row count. Source provenance must record source-root-relative paths, not just filename, to maintain reproducibility.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
