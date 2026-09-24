---
name: crossprovider codex multi-path-ci-routing-can-hide-test-exclusions
description: Multi-path CI routing can hide test exclusions
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ci, workflow-design, testing]
---

Removing a test from one CI invocation path (e.g., direct workflow step) does not exclude it if alternative routing paths exist (e.g., domain matrix, full-suite runs). Verify all code paths that could trigger a test before claiming exclusion.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
