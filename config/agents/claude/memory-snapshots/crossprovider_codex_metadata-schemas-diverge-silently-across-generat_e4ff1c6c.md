---
name: crossprovider codex metadata-schemas-diverge-silently-across-generat
description: Metadata schemas diverge silently across generated outputs
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [generated-outputs, metadata-schema, cross-output-validation]
---

When multiple outputs reference the same entity (e.g., ABS source), metadata fields are often inconsistent: page frontmatter includes `revision, artifact_sha256, provenance_level`; queue CSVs include `source_id, citation_slug` but omit the revision/artifact fields; logs omit even more. Per-output validation passes; cross-output variance is invisible. Define a canonical metadata schema for each entity and validate every output against it (not per-output validation in isolation). In #267/#268, provenance fields were missing from queue/log outputs while present in pages.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
