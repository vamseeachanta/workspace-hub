---
name: crossprovider codex enforcement-metadata-without-runtime-consumers-b
description: Enforcement metadata without runtime consumers becomes advisory-only
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [config-patterns, gates-and-contracts, implementation-gaps]
---

Declaring a field `required` in a config schema doesn't enforce it unless the stage runner/verifier actually consumes it. YAML annotations are documentation, not gates. If enforceability is intended, add mechanical checks in the runner or downgrade to `advisory`.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
