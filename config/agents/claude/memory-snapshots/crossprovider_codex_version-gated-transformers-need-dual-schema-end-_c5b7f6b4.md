---
name: crossprovider codex version-gated-transformers-need-dual-schema-end-
description: Version-gated transformers need dual-schema end-to-end tests
metadata:
  type: reference
  source: codex
  bridged: 2026-07-27
  tags: [schema-versioning, multi-stage-testing, version-gates, compatibility]
---

A tight schema-version gate (e.g., `if schema_version == 4: accept else: reject`) in a transformation step silently breaks when the producer upgrades. Fix: tests must verify both old and new schema data flow correctly through the full pipeline, not just assert each stage in isolation. Provider-row verdicts here failed on schema 5 despite collector-only tests passing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
