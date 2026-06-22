---
name: crossprovider codex public-facing-generated-json-leaks-private-artif
description: Public-facing generated JSON leaks private artifact paths and raw labels
metadata:
  type: reference
  source: codex
  bridged: 2026-06-21
  tags: [generated-artifacts, data-leakage, schema-enforcement]
---

Generated reports emit `source_queue`/`source_queue_report` filenames and `labels` arrays with machine/agent/domain/lane identifiers in supposedly opaque public payloads. Stricter output schemas and public-surface diffing required; constrain generator output to opaque IDs, enums, counts, issue refs only.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
