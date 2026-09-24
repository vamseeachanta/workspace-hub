---
name: crossprovider codex stage-contract-enforcement-p1-gap-rules-require-
description: Stage contract enforcement: P1-gap rules require mechanical validation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [stage-contract, validator, contract-enforcement]
---

When a stage defines a P1-gap forcing rule ('unresolved P1 → pause_and_revise'), the summary artifact must validate this invariant before allowing 'continue' decisions. Violating this creates a self-contradictory contract. Add validator hooks to check the invariant before accepting pass decisions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
