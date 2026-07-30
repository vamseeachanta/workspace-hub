---
name: crossprovider codex hash-contracts-require-explicit-preimage-specifi
description: Hash contracts require explicit preimage specifications
metadata:
  type: reference
  source: codex
  bridged: 2026-07-19
  tags: [specification, reproducibility, hash-contract, cryptography]
---

Statements like 'canonical JSON, sorted keys, stable types' do not define a hash contract. Must explicitly specify: number format (int/float rendering), Unicode normalization form, null handling, enum encoding, decimal precision, schema version pinning, field exclusions (self-hash, timestamps), path case sensitivity. Omitting these allows valid implementations to diverge, breaking reproducibility.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
