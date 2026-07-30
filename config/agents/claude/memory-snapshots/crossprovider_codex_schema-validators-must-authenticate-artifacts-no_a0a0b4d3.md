---
name: crossprovider codex schema-validators-must-authenticate-artifacts-no
description: Schema validators must authenticate artifacts, not just syntax-check
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [validation, security, schema]
---

Synthetic fixture integration showed syntax-only validators accept mutable refs, fake digests, and overclaims. Add cryptographic framing (checksum auth, manifest-last pattern, signed serialization) to enforce artifact immutability and reject overclaiming.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
