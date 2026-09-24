---
name: crossprovider codex attestation-must-occur-immediately-before-return
description: Attestation must occur immediately before return
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [race-condition, atomicity, validation, toctou]
---

Validate/attest final state immediately before function return, not before cleanup operations. Concurrent mutation between validation and return can evade checks. Attestation is the final operation; cleanup (closing descriptors, removing temporaries) follows, then return.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
