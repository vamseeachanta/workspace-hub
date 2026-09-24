---
name: crossprovider codex authority-vs-evidence-distinction-in-validation
description: Authority vs Evidence distinction in validation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, validation, trust-model, authority]
---

External systems produce evidence, not authority. Reconstruct expected state from separately-supplied trusted inputs (registry, snapshot, configuration) and compare; never accept serialized results from external publishers as correct. This prevents forged or mutated external claims.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
