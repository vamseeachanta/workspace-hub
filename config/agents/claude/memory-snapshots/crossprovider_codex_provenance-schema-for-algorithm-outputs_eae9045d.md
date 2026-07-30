---
name: crossprovider codex provenance-schema-for-algorithm-outputs
description: Provenance schema for algorithm outputs
metadata:
  type: reference
  source: codex
  bridged: 2026-07-10
  tags: [architecture, provenance, output-specification]
---

Pattern: `Provenance.{sources[], code_version}` + `CitedValue.{value, citation, units}` + `DataSource.{kind, identifier, digest, retrieved_at}` together capture output traceability. Code version as short-hex should be proven to map to a Git commit; outputs lacking this structure fail closed in fail-closed report assembly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
