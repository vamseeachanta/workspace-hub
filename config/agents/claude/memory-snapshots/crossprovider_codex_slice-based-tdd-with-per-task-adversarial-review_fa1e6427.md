---
name: crossprovider codex slice-based-tdd-with-per-task-adversarial-review
description: Slice-based TDD with per-task adversarial review catches schema defects early
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tdd, review-workflow, schema-validation, defect-prevention]
---

The #1039 implementation split work into small tasks (schema, fixtures, reconciliation), each with RED tests and independent review. Reviews caught real defects: foreign-key fail-open, incompatible interval semantics, unknown-asset representation gaps. This pattern proved effective for multi-contract work where schema interactions are non-obvious.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
