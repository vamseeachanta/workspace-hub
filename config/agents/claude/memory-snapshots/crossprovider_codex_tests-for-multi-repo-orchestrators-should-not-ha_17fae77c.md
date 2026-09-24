---
name: crossprovider codex tests-for-multi-repo-orchestrators-should-not-ha
description: Tests for multi-repo orchestrators should not hardcode workspace layout while claiming fixture independence
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, fixtures, test-design]
---

Tests that mock the external tool (e.g., `uv`) but still depend on real workspace repo paths and actual `pyproject.toml` files are weak: they will miss environment-specific failures and repo-specific config problems. Either use fixture repos throughout or acknowledge that the test is integration-level.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
