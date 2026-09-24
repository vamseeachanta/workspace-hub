---
name: crossprovider codex vague-interface-contracts-are-unimplementable
description: Vague interface contracts are unimplementable
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [interface-design, contract-specification, extensibility]
---

Interfaces for extensible systems (evaluators, plugins, handlers) with illustrative return shapes like `{warnings, criticals, findings, score?}` do not translate to working code. Must specify upfront: required fields, types, severity semantics, deterministic decision rules, and edge-case behavior. Observed across 3 review iterations of #2408 evaluator interface.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
