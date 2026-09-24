---
name: crossprovider codex read-only-post-fix-adversarial-review-validates-
description: Read-only post-fix adversarial review validates blocker resolution without re-execution
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [review, read-only, post-fix-verification, artifact-validation]
---

When re-reviewing after fixes in a read-only context, inspect file:line diffs + artifact evidence (generated data, manifests) + prior test pass history; do not re-execute. Example: worldenergydata #663 verified filed-month horizon, chunk carryover, null metric gaps, and operator rollup via direct code inspection + CSV artifact validation, deferring to passing test evidence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
