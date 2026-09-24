---
name: crossprovider codex expected-failure-allowlists-need-repo-scope-reas
description: Expected-failure allowlists need repo scope, reason, and expiry metadata beyond exact node IDs
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [test-maintenance, parametrized-tests, allowlist-hygiene, WRK-1054]
---

Storing only exact pytest node IDs in expected-failure lists is brittle for parametrized tests, renamed files, and refactors. Include repo scope, failure reason, and last-confirmed timestamp or expiry date so the allowlist can be audited and decayed over time rather than becoming stale technical debt.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
