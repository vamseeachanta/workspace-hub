---
name: crossprovider codex public-artifact-generation-requires-schema-versi
description: Public artifact generation requires schema versioning, conservative derivation, and multi-gate validation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [artifact-generation, public-safety, schema-versioning, validation-gates]
---

Public-safe knowledge graph generation (issue #77) uses versioned schema (`public-graph/v1`), conservative relation derivation (inferred relationships must never become edges), deterministic generation, and three-level validation: targeted pytest + full pytest + custom validator (path sanitization, safety diagnostics). Unresolved targets are dropped, not preserved; cross-domain diagnostics are metadata hints only, never edge sources.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
