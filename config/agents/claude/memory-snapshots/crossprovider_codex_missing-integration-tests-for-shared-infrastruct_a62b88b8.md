---
name: crossprovider codex missing-integration-tests-for-shared-infrastruct
description: Missing integration tests for shared infrastructure (hooks, enforcement scripts, shared libs) are blocking gaps
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [testing, integration-gaps, shared-infrastructure]
---

Plans modifying pre-commit hooks, enforcement scripts, or shared libraries must include end-to-end wiring tests, not just unit tests of the new code. Codex found plans adding skill-health-dashboard wiring without testing the integration, and enforcer scripts without harness contract tests. These are high-risk gaps.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
