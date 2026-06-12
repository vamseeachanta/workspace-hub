---
name: crossprovider codex tdd-claims-must-distinguish-inventory-checks-fro
description: TDD claims must distinguish inventory checks from behavioral regression tests
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [plan-review, testing, tdd]
---

Plans overstate 'tests before implementation' when they list lint/structure/inventory checks (`test_inventory_groups_top_rule_families`) but lack behavioral regression tests for touched modules. Lint validation ≠ behavior-preservation tests for source edits; both are required for sufficient TDD gate.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
