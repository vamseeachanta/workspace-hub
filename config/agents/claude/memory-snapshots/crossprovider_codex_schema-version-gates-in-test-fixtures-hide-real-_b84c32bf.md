---
name: crossprovider codex schema-version-gates-in-test-fixtures-hide-real-
description: Schema version gates in test fixtures hide real regressions
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [testing, schema-migration, fixtures]
---

The equality-matrix provider-capability test fixture was pinned to schema 4 while the collector now emits schema 5. The hard version gate (`provider_row_verdict()` only accepts `schema_version == 4`) caused tests to pass locally but rendered all provider rows as `MISSING-EVIDENCE` in production. Fixture schema must track production schema; version gates should accept a range or be tested with actual schema transitions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
