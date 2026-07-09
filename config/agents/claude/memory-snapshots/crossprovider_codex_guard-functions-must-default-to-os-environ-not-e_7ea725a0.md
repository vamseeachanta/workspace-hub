---
name: crossprovider codex guard-functions-must-default-to-os-environ-not-e
description: Guard functions must default to os.environ, not empty dict
metadata:
  type: reference
  source: codex
  bridged: 2026-07-02
  tags: [guard-pattern, environment-variables, testing-isolation, security]
---

When a guard function accepts an optional `env` parameter for testing, defaulting to `{}` instead of `os.environ` causes the guard to bypass real environment checks in CLI/production paths. The correct pattern: pass `env` explicitly in tests, read `os.environ` as the default when `env` is omitted, never default to empty state.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
