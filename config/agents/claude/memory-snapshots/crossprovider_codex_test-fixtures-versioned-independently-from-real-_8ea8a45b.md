---
name: crossprovider codex test-fixtures-versioned-independently-from-real-
description: Test fixtures versioned independently from real collectors create silent breakage
metadata:
  type: reference
  source: codex
  bridged: 2026-07-25
  tags: [testing, fixtures, schema-versioning, parity-checks]
---

When test fixtures diverge from the real collector's output format (here: fixtures locked at schema 4, collector emitting schema 5), tests pass but production code breaks. For schema-aware code, tests must use `_provider_report()` or fixtures with the SAME version the real collector emits, not a convenient old version.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
