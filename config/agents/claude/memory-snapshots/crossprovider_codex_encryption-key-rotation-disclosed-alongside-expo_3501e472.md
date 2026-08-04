---
name: crossprovider codex encryption-key-rotation-disclosed-alongside-expo
description: Encryption key rotation disclosed alongside exposure in same session
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [security, cryptography, key-management]
---

When a private key is rotated in response to exposure, both old and new keys can end up in the same session transcript if the new key is generated and sent within that session. Requires out-of-band distribution or pre-generated rotation candidates.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
