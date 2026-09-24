---
name: crossprovider codex fixture-driven-tdd-contract-first-pattern
description: Fixture-driven TDD contract-first pattern
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tdd, testing, methodology]
---

Write pytest fixtures and tests before implementation. Tests initially fail at collection or execution—this failure is the contract, not a problem. Add test data/manifest examples inline. Implementation threads through failing tests until suite passes. Used successfully across OpenFOAM, Blender, and Orcina modules.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
