---
name: crossprovider codex verify-selection-logic-with-adversarial-test-dat
description: Verify selection logic with adversarial test data, not just golden-path tests
metadata:
  type: reference
  source: codex
  bridged: 2026-06-17
  tags: [testing, safety, adversarial-testing, manifests]
---

For manifest-based selection or scope-bounded operations: insert duplicate/out-of-scope rows in test fixtures and verify selection correctness and rejection logic hold. Golden-path tests alone miss drift and boundary defects.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
