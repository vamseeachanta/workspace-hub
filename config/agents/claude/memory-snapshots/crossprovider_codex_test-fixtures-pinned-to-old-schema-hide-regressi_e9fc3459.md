---
name: crossprovider codex test-fixtures-pinned-to-old-schema-hide-regressi
description: Test fixtures pinned to old schema hide regressions in new-format paths
metadata:
  type: reference
  source: codex
  bridged: 2026-07-28
  tags: [testing-blind-spots, schema-migration, test-fixtures]
---

When test fixtures are hardcoded to legacy schema/format but real collectors emit new formats, tests pass while production data silently fails. Keep fixture schemas aligned with what producers actually emit, especially when testing schema evolution paths.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
