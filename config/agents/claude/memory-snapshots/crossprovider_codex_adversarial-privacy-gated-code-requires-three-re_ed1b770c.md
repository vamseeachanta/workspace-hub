---
name: crossprovider codex adversarial-privacy-gated-code-requires-three-re
description: Adversarial privacy-gated code requires three review passes
metadata:
  type: reference
  source: codex
  bridged: 2026-06-25
  tags: [privacy, review, adversarial, governance]
---

Governance pass: check identifier reversibility (can public handles join private data?), commitment/metadata leak paths, and gate placement. Execution pass: verify formal schema, concrete commands, test scope. Diff pass: validate actual artifact content against spec. Single-pass review misses category-specific defects; session #790 plan passed privacy review but failed execution review, then diff review found artifact leaks that all prior tests missed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
