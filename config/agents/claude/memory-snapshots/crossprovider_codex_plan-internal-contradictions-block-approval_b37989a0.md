---
name: crossprovider codex plan-internal-contradictions-block-approval
description: Plan internal contradictions block approval
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [planning, approval-gate, correctness]
---

When a plan has multiple normative sections (pseudocode, acceptance criteria, TDD list) that contradict each other, it cannot be implemented. Common: acceptance requiring file X while scope forbids it; pseudocode assigning status A and B to same record; tests expecting different behavior than pseudocode.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
