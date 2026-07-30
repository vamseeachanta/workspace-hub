---
name: crossprovider codex lock-file-updates-must-be-explicit-in-acceptance
description: Lock file updates must be explicit in acceptance criteria
metadata:
  type: reference
  source: codex
  bridged: 2026-07-05
  tags: [dependency-hygiene, approval, lock-file]
---

When adding new package member to monorepo, uv.lock refresh is not optional; must be explicit in plan acceptance. Conditional/optional lock updates create hidden dependencies and test failures.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
