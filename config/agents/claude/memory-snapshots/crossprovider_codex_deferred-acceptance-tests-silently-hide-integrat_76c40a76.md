---
name: crossprovider codex deferred-acceptance-tests-silently-hide-integrat
description: Deferred acceptance tests silently hide integration failures
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [acceptance-tests, testing-patterns, dependency-management]
---

Acceptance tests that skip when dependencies are missing continue skipping even after blockers land, masking broken integration. After upstream work completes, a skipped acceptance test becomes a false pass. Either fail hard when skip conditions stale, or dynamically fail if the deferred code is still missing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
