---
name: crossprovider codex interior-hash-consistency-cannot-prove-licensed-
description: Interior hash consistency cannot prove licensed solver execution
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [security, verification, licensing]
---

Consistent bundle_sha256 and result_sha256 values can be fabricated in ordinary JSON; they provide integrity but no proof of actual licensed execution. Solver attestation requires cryptographically signed producer identity, verified trust root, and protected ledger binding the result to the licensed host.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
