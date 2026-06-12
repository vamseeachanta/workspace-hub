---
name: crossprovider codex test-fixtures-must-be-deterministic-not-live-rep
description: Test fixtures must be deterministic, not live-repo dependent
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [testing, fixtures, determinism]
---

Tests using real workspace repos for pass/fail assertions are brittle and non-deterministic—they reflect repo state, not script behavior. Create minimal fixture directories or mock commands instead. Validated when live-repo fixtures for mypy, ruff, and pytest silently absorbed environment failures (missing config, unresolved dependencies) that the test harness was meant to catch.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
