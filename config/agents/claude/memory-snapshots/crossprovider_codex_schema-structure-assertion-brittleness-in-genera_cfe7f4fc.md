---
name: crossprovider codex schema-structure-assertion-brittleness-in-genera
description: Schema/structure assertion brittleness in generated code
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [testing-strategy, regression-brittleness, refactoring-risk]
---

Tests asserting exact generated output structure (file names, YAML key placement, include paths) break on internal refactors even when end results remain valid. Prefer behavioral assertions (generated model loads/validates) over structural ones (contains files X, Y, Z with specific names). Structure tests should validate contract interfaces, not implementation partitioning.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
