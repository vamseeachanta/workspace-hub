---
name: crossprovider codex fail-closed-test-coverage-for-data-lifecycle-bou
description: Fail-closed test coverage for data lifecycle boundaries
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, data-lifecycle, security, boundaries]
---

Data-lifecycle tests must verify that unsafe transitions (raw→public, private→public) explicitly fail by default, not just that safe transitions pass. Tests should validate that private/client data cannot auto-promote to public surfaces without explicit gates.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
