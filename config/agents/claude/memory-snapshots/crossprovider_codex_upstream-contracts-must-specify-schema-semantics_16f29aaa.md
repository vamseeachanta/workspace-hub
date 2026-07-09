---
name: crossprovider codex upstream-contracts-must-specify-schema-semantics
description: Upstream contracts must specify schema semantics, not just field names
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [schema-design, contracts, downstream-integration]
---

When one issue (#62) defines a contract that downstream issues (#70) must consume, listing field names is insufficient. Define JSON structure, types, nesting, required/optional rules, and format constraints for complex fields (e.g., snapshot_ids_by_manifest_source, drift_verdicts_by_manifest_source_pair). Prose-only contracts force downstream implementations to guess and break compatibility.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
