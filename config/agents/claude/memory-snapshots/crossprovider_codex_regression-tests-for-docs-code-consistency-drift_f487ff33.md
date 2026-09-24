---
name: crossprovider codex regression-tests-for-docs-code-consistency-drift
description: Regression tests for docs-code consistency drift
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, docs, regression]
---

Add pytest to compare operator docs (e.g., scheduled-tasks.md) against canonical source (schedule YAML). Watch the test fail initially when docs are stale. Fix the docs, validate the regression passes. Prevents silent drift between documentation and implementation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
