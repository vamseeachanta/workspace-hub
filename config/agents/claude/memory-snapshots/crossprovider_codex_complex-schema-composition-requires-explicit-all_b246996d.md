---
name: crossprovider codex complex-schema-composition-requires-explicit-all
description: Complex schema composition requires explicit allowlists and deterministic gates
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema-design, test-coverage, composition-hazard]
---

Publication-state decisions cannot rely on prose conditions like "return private_publishable or blocked". Schema gates must use decision tables mapping state → output residency, and all state transitions must have test fixtures (approved, approved-with-notes, blocked) verifying only allowed states publish to public output.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
