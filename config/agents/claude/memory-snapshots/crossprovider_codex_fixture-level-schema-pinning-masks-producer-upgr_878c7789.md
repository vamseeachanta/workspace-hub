---
name: crossprovider codex fixture-level-schema-pinning-masks-producer-upgr
description: Fixture-level schema pinning masks producer-upgrade regressions
metadata:
  type: reference
  source: codex
  bridged: 2026-07-27
  tags: [schema-versioning, testing-gap, fixture-strategy, pipeline-regressions]
---

When test fixtures mock an older schema version while a producer is upgraded to emit a new version, downstream tests pass locally (mocked data matches old consumer expectations) while real data silently fails. The equality-matrix collector upgraded to schema 5 but build-equality-matrix.py still gates on schema 4; tests passed because _provider_report() pinned fixtures to schema 4, masking that schema-5 provider-harness reports now trigger MISSING-EVIDENCE instead of parity checks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
