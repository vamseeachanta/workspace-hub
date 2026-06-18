---
name: crossprovider codex builder-fail-closed-drift-check-pattern-for-test
description: Builder + fail-closed drift-check pattern for test fixtures
metadata:
  type: reference
  source: codex
  bridged: 2026-06-17
  tags: [testing, builder-pattern, fixtures, drift-detection, fail-closed]
---

Importable builder interface (not CLI defaults) with hard-coded expected identities and drift assertions (exact selected/excluded/missing sets) executed BEFORE payload creation or output write. Fail-closed: unknown/locked extraction states → metadata-only, never ambiguous output. Reusable across resource-extraction tests; originated in electrical-canary (#524).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
