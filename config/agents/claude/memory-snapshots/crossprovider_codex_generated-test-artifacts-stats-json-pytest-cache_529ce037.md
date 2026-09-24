---
name: crossprovider codex generated-test-artifacts-stats-json-pytest-cache
description: Generated test artifacts (stats.json, pytest cache) must be cleaned before diff review
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [test-artifacts, git-hygiene]
---

Local test runs generate artifacts (e.g., `stats.json`, `.pytest_cache/`) that can be unintentionally staged. Clean these before final diff review and commit to keep changesets clean.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
