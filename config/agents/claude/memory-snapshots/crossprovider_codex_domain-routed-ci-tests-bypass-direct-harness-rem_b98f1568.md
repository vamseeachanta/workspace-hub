---
name: crossprovider codex domain-routed-ci-tests-bypass-direct-harness-rem
description: Domain-routed CI tests bypass direct-harness removal
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [ci-routing, regression-prevention, testing]
---

Removing a test from a workflow `.yml` file does not prevent execution if the test is included via domain-matrix routing (e.g., a domain label that pulls `tests-marine-engineering/`). Guards must be implemented within test logic itself, not just in workflow invocation, to prevent nonportable tests from running in incompatible CI environments.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
