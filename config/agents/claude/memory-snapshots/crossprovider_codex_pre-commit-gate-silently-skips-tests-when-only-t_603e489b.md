---
name: crossprovider codex pre-commit-gate-silently-skips-tests-when-only-t
description: Pre-commit gate silently skips tests when only test files are modified
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [pre-commit-hooks, test-gate, coverage-gaps]
---

Source-to-test mapping intentionally returns nothing for test_*.py files, so changes to tests themselves don't trigger test runs. Add explicit test-file detection to the mapping logic or accept this gap in pre-commit coverage.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
