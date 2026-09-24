---
name: crossprovider codex malformed-nested-maps-must-fail-closed-explicitl
description: Malformed nested maps must fail closed explicitly
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, error-handling, fail-closed]
---

Type-check nested data structures (dicts, lists) before iterating or key-accessing them. Early type validation with clear errors prevents silent skips or late crashes; passing a malformed `drift_verdicts_by_manifest_source_pair: []` should reject immediately, not return empty results.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
