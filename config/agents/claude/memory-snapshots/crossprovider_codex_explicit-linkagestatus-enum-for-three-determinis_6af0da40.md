---
name: crossprovider codex explicit-linkagestatus-enum-for-three-determinis
description: Explicit LinkageStatus enum for three deterministic states
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [contracts, state-machines, type-safety]
---

Use enum with three states (`LINKED | UNLINKED | AMBIGUOUS`) instead of boolean or null. Forces explicit edge-case handling in consumers and makes impossible states unrepresentable in the type system.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
