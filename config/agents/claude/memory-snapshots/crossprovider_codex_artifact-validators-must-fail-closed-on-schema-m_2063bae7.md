---
name: crossprovider codex artifact-validators-must-fail-closed-on-schema-m
description: Artifact validators must fail-closed on schema/metadata drift
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [validation, fail-closed, generated-artifacts]
---

Validators for generated artifacts should reject, not accept, stale or mismatched metadata. Fail-closed behavior prevents downstream consumers from using outdated counts, digests, or report contents. Must validate: row counts across JSONL/CSV, field presence, schema version, report date consistency, and list-entry presence (nodes/edges cited in summary must exist in artifact).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
