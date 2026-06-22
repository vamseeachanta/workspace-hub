---
name: crossprovider codex opaque-id-design-must-specify-determinism-not-ju
description: Opaque ID design must specify determinism, not just opacity
metadata:
  type: reference
  source: codex
  bridged: 2026-06-21
  tags: [cryptographic-design, id-schemes, verifiable-proofs]
---

Proof IDs claimed 'opaque' without specifying whether deterministic (hash-based, data-leaking) or random (non-reproducible/non-reviewable). ID designs must state: salted, HMAC'd, collision-checked; tests must verify non-determinism and verify reproducibility only where needed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
