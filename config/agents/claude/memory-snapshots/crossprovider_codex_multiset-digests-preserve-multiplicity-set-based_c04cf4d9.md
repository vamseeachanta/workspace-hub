---
name: crossprovider codex multiset-digests-preserve-multiplicity-set-based
description: Multiset digests preserve multiplicity; set-based matching is unsafe
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [duplicate-detection, data-structures, correctness, llm-wiki-pattern]
---

For duplicate/overlap evidence, use Counter or multiset structures (extension, byte-size, count) instead of sets. Set-based matching can incorrectly mark distinct same-size files as redundant if only one reference file matches. Always test false-duplicate scenarios: same extension and byte size, different identity, must not trigger delete-candidate recommendation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
