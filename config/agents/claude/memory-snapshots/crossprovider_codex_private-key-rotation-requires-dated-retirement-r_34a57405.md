---
name: crossprovider codex private-key-rotation-requires-dated-retirement-r
description: Private key rotation requires dated retirement records
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [security, operations, key-management]
---

After private key exposure, rotate immediately and back up the retired key with a timestamp. Old keys must be marked RETIRED-[DATE] and verified absent from world-readable paths and git repos.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
