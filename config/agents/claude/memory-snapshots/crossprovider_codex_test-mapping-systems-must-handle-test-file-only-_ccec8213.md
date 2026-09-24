---
name: crossprovider codex test-mapping-systems-must-handle-test-file-only-
description: Test mapping systems must handle test-file-only changes
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, ci-cd, test-discovery, false-confidence]
---

A test mapper that silently returns nothing when only test files (matching `test_*.py` or `*_test.py`) are modified breaks the pre-commit gate—modified tests never run. Ensure mappers detect test file changes and either run those tests or have explicit logic to skip them intentionally.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
