---
name: crossprovider codex multi-version-schema-composition-needs-explicit-
description: Multi-version schema composition needs explicit merge semantics
metadata:
  type: reference
  source: codex
  bridged: 2026-07-19
  tags: [schema-composition, versioning, contract-design]
---

When v1 base and v3 extension both define the same identity key (e.g., handoff from→to→condition), appending violates uniqueness constraints while replacement loses either base or v3 fields. Define field-union strengthening, conflict resolution rules, or replacement semantics before merging.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
