---
name: crossprovider codex structural-evaluation-closes-attestation-bypasse
description: Structural evaluation closes attestation bypasses; reject substring authority
metadata:
  type: reference
  source: codex
  bridged: 2026-07-13
  tags: [security, parsing, evaluation, correctness]
---

Critical attestations (fingerprints, mutation identity, ownership classification) using substring matching can be evaded by reordering, embedding, or literal-sentinel abuse. Use closed evaluator sets with exhaustiveness proofs and adversarial tests for evasion techniques (e.g., `&&` or `||` same-line forms).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
