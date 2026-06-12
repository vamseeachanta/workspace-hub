---
name: crossprovider hermes unsigned-evidence-blobs-enable-cross-machine-for
description: Unsigned evidence blobs enable cross-machine forgery attacks
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [security, multi-machine, evidence-schema, fail-closed]
---

When distributing readiness evidence across machines via shared directories, pure JSON assertions (no signatures, MACs, or cryptographic binding) allow any actor with write access to mint false "pass" verdicts for arbitrary hosts. This bypasses all subsequent validation gates. For multi-machine dispatch, evidence schema must include HMAC/signature keyed to a shared secret or host-local key material.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
