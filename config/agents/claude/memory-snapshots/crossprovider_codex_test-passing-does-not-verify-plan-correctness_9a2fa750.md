---
name: crossprovider codex test-passing-does-not-verify-plan-correctness
description: Test passing does not verify plan correctness
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, verification, review, plan-correctness]
---

Unit tests can pass (happy path, schema validation) while plans have correctness gaps (edge cases, boundary conditions, assumption verification). Integration verification + adversarial reading + generated-artifact inspection are required before declaring plan correctness.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
