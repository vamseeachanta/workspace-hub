---
name: crossprovider codex regression-boundaries-must-be-explicitly-marked-
description: Regression boundaries must be explicitly marked in files-to-change
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [scope-boundaries, regression-testing]
---

Mark existing files as 'verify only', 'no-change', or 'regression-boundary' rather than omitting them implicitly. This prevents scope creep into parent contracts and makes the change contract boundary clear.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
