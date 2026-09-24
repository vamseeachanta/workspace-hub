---
name: crossprovider codex tests-must-follow-repo-s-pytest-discovery-conven
description: Tests must follow repo's pytest discovery convention, not package-local paths
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, conventions, configuration]
---

Tests must live in paths that pytest is configured to discover (typically tests/ root level) and not assume discovery from package-internal locations. Verify pyproject.toml testpaths setting; package-local test paths may never be discovered.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
