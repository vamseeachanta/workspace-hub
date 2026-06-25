---
name: crossprovider codex test-environment-secrets-leak-in-failure-stack-t
description: Test environment secrets leak in failure stack traces
metadata:
  type: reference
  source: codex
  bridged: 2026-06-24
  tags: [testing, security, env-variables]
---

When tests depend on ambient sensitive data (cryptographic keys, exact source labels, tokens), pytest will expose that data in failure messages and tracebacks if the environment variable is absent or assertion fails. Use synthetic test fixtures or self-contained test data instead of real sensitive values in test assertions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
