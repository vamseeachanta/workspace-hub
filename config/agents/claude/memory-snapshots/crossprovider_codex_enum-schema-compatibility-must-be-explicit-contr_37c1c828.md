---
name: crossprovider codex enum-schema-compatibility-must-be-explicit-contr
description: Enum/schema compatibility must be explicit contract, not deferred risk
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [contract, schema, risk-acceptance]
---

When a plan proposes changing enums or schemas that differ from current producer output (e.g., scorecard freshness values), the plan must explicitly define the mapping/migration path. Leaving it as a 'risk' defers the critical decision and allows incompatible implementations to slip through review. Concrete: if scorecard emits 'empty'/'sample'/'full' but plan proposes different enum, contract must define transformation or assert which side changes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
