---
name: crossprovider gemini regression-tests-must-iterate-over-lists-not-har
description: Regression tests must iterate over lists, not hardcode
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [testing, regression-coverage, loop-patterns]
---

Tests checking for absence of 10 deleted items by hardcoding 2 misses the other 8. Use dynamic iteration over a manifest list (e.g., `DELETED_DIRS`) to catch all regressions with one loop.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
