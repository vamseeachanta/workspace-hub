---
name: crossprovider codex deterministic-generation-requires-case-hash-and-
description: Deterministic generation requires case hash and version metadata
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [reproducibility, determinism, testing]
---

Generators that produce byte-for-byte repeatable output (e.g., OrcaFlex modular model generator) must emit and return canonical case hash, input hashes, solver version, and generated-file hashes. Absence of this metadata blocks reproducibility validation and makes result transport lossy.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
