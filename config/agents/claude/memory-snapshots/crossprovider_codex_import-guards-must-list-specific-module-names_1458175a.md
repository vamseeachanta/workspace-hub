---
name: crossprovider codex import-guards-must-list-specific-module-names
description: Import guards must list specific module names
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [import-guards, lazy-loading, testing]
---

Tests forbidding eager imports (e.g., scheduler cli startup) must explicitly add the module name to forbid lists, not rely on prefix patterns. Prefix-match tests that don't include worldenergydata.scheduler.jobs.spain_cores_refresh will not catch violations if imports added later.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
