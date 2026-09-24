---
name: crossprovider codex underspecified-field-semantics-and-cli-contracts
description: Underspecified field semantics and CLI contracts make adversarial testing ineffective
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning, testing, specifications]
---

Plans that define required fields or CLI flags without closed semantics (allowed values, state transitions, null handling) force implementations to guess behavior. Tests can only verify presence, not correctness. Before implementing, enumerate all field enum values, format constraints, CLI argument validation rules, and success/failure criteria. Otherwise red-test-first development is impossible.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
