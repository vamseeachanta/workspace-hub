---
name: crossprovider codex schemas-must-support-explicit-unknown-types
description: Schemas must support explicit unknown types
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [schema-design, forward-compatibility, type-systems]
---

Implicit unknowns and placeholder coercion fail when a schema must represent true 'unknown' states (e.g., unconfirmed quantities). Use explicit union types (e.g., `positive_int | 'unknown'`) to support the full semantic space.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
