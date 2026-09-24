---
name: crossprovider codex parametrized-test-fixtures-with-shared-state-lea
description: Parametrized test fixtures with shared state leak coverage
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, fixtures, parametrization]
---

Shared fixture state (e.g., unshallow) can carry from one parametrized case to the next, causing subsequent cases to pass by accident. Isolate fixtures per parametrization and assert preconditions (e.g., shallow repo, one-parent HEAD) before the SUT.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
