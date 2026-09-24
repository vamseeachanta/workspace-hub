---
name: crossprovider codex internal-contradictions-between-tdd-rows-and-pla
description: Internal contradictions between TDD rows and plan policy statements
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [test-design, internal-consistency, adversarial-review]
---

Test expectations can contradict the plan's own stated policy (e.g., a TDD test expecting 'drop field X' while the task policy says 'preserve field X'). Check TDD rows against the detailed task descriptions and scope boundaries; internal inconsistencies are easy to miss in textual review.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
