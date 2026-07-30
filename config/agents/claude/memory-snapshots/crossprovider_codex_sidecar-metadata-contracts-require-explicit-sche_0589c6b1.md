---
name: crossprovider codex sidecar-metadata-contracts-require-explicit-sche
description: Sidecar/metadata contracts require explicit schema before implementation
metadata:
  type: reference
  source: codex
  bridged: 2026-07-06
  tags: [schema-design, metadata, contracts]
---

When introducing JSON sidecars or enrichment metadata, define exact JSON schema, validation rules for missing/malformed cases, and how downstream consumers verify/validate before defaulting. Undefined contracts create silent failures when sidecars are absent or don't match consumer expectations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
