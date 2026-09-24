---
name: crossprovider codex test-setup-invocation-failures-silently-pass-whe
description: Test setup invocation failures silently pass when exit status is not checked
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, shell-safety, error-handling, test-validity]
---

Test harnesses that call external commands without verifying exit status (e.g., detector invocation in fixture setup) can swallow failures and produce false-passing suites. Always check `$?` or use `set -e` discipline for test-command invocations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
