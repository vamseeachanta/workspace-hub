---
name: crossprovider codex hard-schema-version-gates-silently-reject-upgrad
description: Hard schema-version gates silently reject upgraded data
metadata:
  type: reference
  source: codex
  bridged: 2026-07-23
  tags: [schema-versioning, backward-compatibility, test-coverage-gap, invisible-regression]
---

A collector emitting schema 5 while validators accept only `schema_version == 4` causes all new data to render as `MISSING-EVIDENCE`; tests pass because they only exercise the old path. Versioning gates should accept compatible upgrades (e.g., `>= 4`) or maintain dual fixtures covering both versions to catch regressions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
