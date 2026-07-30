---
name: crossprovider codex fixture-commit-audit-stale-tests-encode-intent-t
description: Fixture commit audit: stale tests encode intent to maintainers
metadata:
  type: reference
  source: codex
  bridged: 2026-07-08
  tags: [testing, fixtures, code-review]
---

When committing a fixture update, audit tests that encode the old behavior even if no current code path invokes them. Stale tests signal to maintainers that legacy fallback is supported/intended, misleading future decisions. Remove or update them explicitly before merging.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
