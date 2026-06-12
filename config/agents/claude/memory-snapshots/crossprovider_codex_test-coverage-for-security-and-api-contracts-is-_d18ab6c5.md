---
name: crossprovider codex test-coverage-for-security-and-api-contracts-is-
description: Test coverage for security and API contracts is often missing
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [testing, security, api-contracts]
---

Security edge cases (path traversal, injection) and API contract violations (invalid factors, out-of-range parameters) are frequently discovered by human code review, not caught by test suites. These require explicit coverage targets, not assumed by general tests.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
