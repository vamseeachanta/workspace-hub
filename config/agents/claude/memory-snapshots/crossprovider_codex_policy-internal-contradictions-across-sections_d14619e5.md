---
name: crossprovider codex policy-internal-contradictions-across-sections
description: Policy internal contradictions across sections
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [policy-review, internal-consistency, state-machines]
---

Policies defining state machines, precedence rules, or enums often contradict themselves across different sections (e.g., 'approval_later always wins' versus 'revert outranks approval'). Require single normative contracts for state/precedence and verify consistency across all referencing sections before approval.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
