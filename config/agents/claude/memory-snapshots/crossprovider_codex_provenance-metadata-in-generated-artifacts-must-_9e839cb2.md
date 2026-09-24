---
name: crossprovider codex provenance-metadata-in-generated-artifacts-must-
description: Provenance metadata in generated artifacts must be runtime-derived, not hard-coded
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [artifact-generation, metadata, governance, context-awareness]
---

When code generates downstream artifacts (WRK items, reports, etc.) that include provenance metadata (machine name, provider, user), derive these from actual runtime context. Hard-coded values make the artifact generator brittle to environment changes and multi-actor scenarios, breaking governance routing and traceability.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
