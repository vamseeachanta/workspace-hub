---
name: crossprovider codex fail-closed-schema-validation-requires-bypass-pa
description: Fail-closed schema validation requires bypass-path test coverage
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema-validation, testing, security]
---

A validator that rejects source-like keys only when the value is a digest allows those keys to pass with placeholder values. Test suite must cover both the realistic case (raw-digest values) and the bypass case (placeholder values) to ensure the scan is actually fail-closed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
