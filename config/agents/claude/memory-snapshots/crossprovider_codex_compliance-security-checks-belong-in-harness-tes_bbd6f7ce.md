---
name: crossprovider codex compliance-security-checks-belong-in-harness-tes
description: Compliance/security checks belong in harness tests, not domain matrix
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [ci, compliance, security]
---

Cross-cutting concerns like client-identifier regression tests and legal scans run in the ci-harness-tests job, not per-domain. Centralizes compliance checks and prevents them from being skipped by selective domain matching.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
