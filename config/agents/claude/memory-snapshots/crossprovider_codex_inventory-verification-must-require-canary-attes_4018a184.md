---
name: crossprovider codex inventory-verification-must-require-canary-attes
description: Inventory verification must require canary attestation
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [verification-order, ledger-binding, attestation]
---

A ledger can be created directly from snapshot provenance without requiring successful canary verification, bypassing integrity checks. Canary verification must produce an immutable artifact bound to snapshot/config/code/key digests; require and validate this artifact before any ledger creation or resume.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
