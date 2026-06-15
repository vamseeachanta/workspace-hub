---
name: crossprovider codex vacuous-test-assertions-in-shell-test-suites
description: Vacuous test assertions in shell test suites
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [testing, shell-scripting, test-quality]
---

Shell tests ending with || true (fail-open) can pass without proving intended behavior. Assertions succeeding vacuously (empty output when expecting a value) hide regressions. Review Bats assertions for proof of actual behavior, not just exit-status masking.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
