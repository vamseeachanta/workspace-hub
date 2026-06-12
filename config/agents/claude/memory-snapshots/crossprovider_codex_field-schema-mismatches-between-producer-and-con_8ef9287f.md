---
name: crossprovider codex field-schema-mismatches-between-producer-and-con
description: Field schema mismatches between producer and consumer silently drop data
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [data-pipeline, schema-evolution, silent-failures]
---

When index writes `symbol` but code reads `name`, all lookups return empty strings not errors. Schema divergence is invisible until results are tested. Normalize field names on load and add round-trip validation: producer writes field X, consumer reads field X, cross-version compatibility tests verify both.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
