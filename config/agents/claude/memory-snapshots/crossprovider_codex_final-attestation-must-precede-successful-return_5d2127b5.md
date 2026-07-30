---
name: crossprovider codex final-attestation-must-precede-successful-return
description: Final attestation must precede successful return
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [validation, atomicity, timing, race-window]
---

Validation/authorization must complete immediately before operation success, with no intervening descriptor closure or cleanup operations. Closing descriptors between validation and return creates a mutation window where concurrent replacements can occur. Attestation is the final operation before return.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
