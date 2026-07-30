---
name: crossprovider codex adversarial-plan-review-must-verify-bidirectiona
description: Adversarial plan review must verify bidirectional schema/contract-to-task mapping
metadata:
  type: reference
  source: codex
  bridged: 2026-07-18
  tags: [planning, schema-design, contract-consistency]
---

Plans hide major defects when public interface contracts don't align with task boundaries (declared interfaces omitted from implementation tasks, upstream schemas that selection files can't satisfy). Verification requires checking both directions: interfaces→tasks and tasks→artifacts produced.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
