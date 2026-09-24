---
name: crossprovider codex generated-metadata-must-emit-actual-runtime-poli
description: Generated metadata must emit actual runtime policy, not hard-coded defaults
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [metadata, provenance, correctness]
---

When a generator writes manifest, metadata, or configuration artifacts, hard-coded selection limits/policies make the output lie about what was actually applied. Manifest metadata fields must record actual runtime parameters from the execution context, not default/template values. This is especially critical for dossier/ingestion metadata that downstream consumers use to verify completeness.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
