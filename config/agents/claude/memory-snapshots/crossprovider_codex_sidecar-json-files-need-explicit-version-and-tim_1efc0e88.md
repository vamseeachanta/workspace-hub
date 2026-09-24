---
name: crossprovider codex sidecar-json-files-need-explicit-version-and-tim
description: Sidecar JSON files need explicit version and timestamp fields
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [metadata, versioning, schema-design]
---

When creating durable JSON sidecars (e.g., density_factors.json), include schema_version, generated_at, and registry_version fields to enable validation, reconciliation, and audit trails. Lack of versioning makes it impossible to detect stale or mismatched sidecars.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
