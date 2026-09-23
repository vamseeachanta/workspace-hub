---
name: crossprovider codex lookup-contract-mismatch-validation-at-different
description: Lookup contract mismatch: validation at different layers causes ValueError
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [data-contract, lookup, validation]
---

If packaged catalog data has blank required keys, extraction accepts them but lookup validates every row and raises ValueError on queries. This violates the lookup contract (should return empty or KeyError). Always validate at extraction time to ensure downstream lookup behavior matches its public contract.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
