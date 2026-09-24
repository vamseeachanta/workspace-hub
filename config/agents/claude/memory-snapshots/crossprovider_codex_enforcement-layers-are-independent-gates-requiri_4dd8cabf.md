---
name: crossprovider codex enforcement-layers-are-independent-gates-requiri
description: Enforcement layers are independent gates requiring integration tests
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [enforcement, testing, governance, integration-testing]
---

Multi-layer enforcement (runtime hook, commit gate, push gate, cross-review hook, CI gate) creates a false sense of coverage if only unit-tested per layer. Must test the integrated chain: verify that a bypass-attempt at any layer is caught by the full sequence, not just one gate.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
