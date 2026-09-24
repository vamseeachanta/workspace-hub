---
name: crossprovider codex hash-preimage-specifications-incomplete-without-
description: Hash preimage specifications incomplete without platform canonicalization rules
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [hashing, determinism, specification-precision]
---

Cross-platform hashes require explicit definitions for: number rendering (precision, exponent format), Unicode normalization, null encoding, enum representation, self-field exclusion (e.g., whether bundle_sha256 hashes exclude the bundle field itself), timestamp treatment in signed attestations. 'Stable scalar types' and 'canonical UTF-8' are insufficient.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
