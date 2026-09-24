---
name: crossprovider codex metadata-classification-in-multi-format-storage-
description: Metadata classification in multi-format storage systems prevents data integrity violations
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [metadata, data-integrity, multi-format-storage]
---

When storage/scheduler systems store both primary payloads (CSV) and metadata sidecars (JSON) in the same directory without type-based metadata splits (e.g., `format: "csv", sidecar_files: [...] ` vs. treating all files as `format: "csv"`), downstream consumers cannot distinguish them and may treat sidecars as primary data.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
