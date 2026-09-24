---
name: crossprovider codex cross-plan-api-surface-verification-is-required-
description: Cross-plan API surface verification is required for interdependent plans
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-consistency, api-contracts, verification]
---

When multiple plans reference the same APIs, functions, or data models, they must cross-verify assumptions about signatures, optional parameters, and fallback behavior. Plans can contradict each other or the implementation. Example: plans disagreed on whether spec_path was required or optional in OrcaWaveRunner.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
