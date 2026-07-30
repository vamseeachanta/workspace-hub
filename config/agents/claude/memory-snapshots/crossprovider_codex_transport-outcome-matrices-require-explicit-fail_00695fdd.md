---
name: crossprovider codex transport-outcome-matrices-require-explicit-fail
description: Transport outcome matrices require explicit failure-case tests
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [testing, distributed-systems, transport-robustness]
---

A matrix composing push outcomes (timeout, exception, credential-unavailable, accepted-after-retry) is inert if all tests mock success. Reconciliation logic and retry branches are never exercised. Create explicit test cases for each outcome branch, not just happy path.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
