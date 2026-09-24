---
name: crossprovider codex provisional-fixtures-require-explicit-gating-in-
description: Provisional fixtures require explicit gating in plans
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [fixtures, test-readiness, blocking-issues, contracts]
---

When test fixtures are marked `provisional_fixture_contract: true`, note in the plan that transition is blocked by an upstream issue (e.g., awaiting public-output gate). Don't treat provisional fixtures as stable test inputs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
