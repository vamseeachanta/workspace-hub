---
name: crossprovider gemini pytest-collection-skip-lists-must-be-explicit-an
description: Pytest collection skip lists must be explicit and maintained
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [pytest, ci-cd]
---

The `pytest_ignore_collect` hook only skips paths you explicitly list; tests that fail collection but aren't in that list will still be collected and fail. When a file should never run, add it to the skip hook immediately, don't assume it won't be collected.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
