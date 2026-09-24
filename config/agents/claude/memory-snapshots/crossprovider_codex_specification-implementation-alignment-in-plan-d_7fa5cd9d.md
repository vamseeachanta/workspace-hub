---
name: crossprovider codex specification-implementation-alignment-in-plan-d
description: Specification/implementation alignment in plan deliverables
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning, execution, tdd, specification]
---

Plans claiming test coverage or dependencies (e.g., 'test batch 001-003 regression') must either declare unimplemented dependencies as blockers or narrow scope to executable claims. Do not silently skip promised deliverables if their dependencies are not yet done.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
