---
name: crossprovider codex producer-consumer-schema-incompatibilities-must-
description: Producer/consumer schema incompatibilities must be explicitly reconciled before implementation
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [schema-design, contract-alignment, multi-producer-systems]
---

When multiple upstream producers feed a single consumer, all schemas must be explicitly compatible and reconciled. Self-contradictory examples or incompatible field sets between producers block coherent validator implementation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
