---
name: crossprovider codex sensitive-pattern-tests-required-for-unknown-und
description: Sensitive-pattern tests required for unknown/undeclared root names
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [test-coverage, pattern-detection, privacy-control]
---

Tests that only check public or explicitly allowed roots will miss crawling on names matching client/private patterns (client-c, mkt-a, lng-a, etc.). Add pattern-based tests that fail if roots matching sensitive name conventions are inspected or traversed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
