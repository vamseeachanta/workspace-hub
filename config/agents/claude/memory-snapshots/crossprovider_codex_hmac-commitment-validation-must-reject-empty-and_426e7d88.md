---
name: crossprovider codex hmac-commitment-validation-must-reject-empty-and
description: HMAC/commitment validation must reject empty and placeholder keys
metadata:
  type: reference
  source: codex
  bridged: 2026-06-23
  tags: [security, validation, cryptography]
---

When using HMAC or cryptographic commitments as data boundaries, fail-closed validation should reject empty, whitespace-only, and placeholder values—not just missing env vars. Test that the validator catches test-only keys and refuses to start.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
