---
name: crossprovider codex generated-artifact-schema-must-record-input-prov
description: Generated artifact schema must record input provenance for reproducibility
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [ingest, schema, reproducibility, artifacts]
---

Manifest/report outputs should embed input file paths, command arguments, git refs, and content hashes—not just output counts. Downstream phases cannot verify or regenerate without knowing exact inputs used to produce the output.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
