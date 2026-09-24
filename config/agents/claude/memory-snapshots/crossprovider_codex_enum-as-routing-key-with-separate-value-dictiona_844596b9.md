---
name: crossprovider codex enum-as-routing-key-with-separate-value-dictiona
description: Enum-as-routing-key with separate value dictionary pattern
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, enums, routing]
---

When domain enums serve as dispatch keys, numeric or SI values may live in a separate dictionary rather than as enum member values. In mooring work, `MooringCondition` is a string enum (`INTACT_QUASI_STATIC = "intact-quasi-static"`) with numeric safety factors in `_MOORING_SAFETY_FACTORS` dict lookup. Code reviewers and plan authors often assume enum members ARE the values; verify indirection.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
