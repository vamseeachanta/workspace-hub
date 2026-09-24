---
name: crossprovider codex licensed-solver-attestation-needs-cryptographic-
description: Licensed solver attestation needs cryptographic binding, not hashes alone
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [licensing, attestation, solver-verification, cryptographic-binding]
---

Hashes verify data integrity but not that the solver ran. Fabricated results can satisfy semantic checks and hash consistency. Require authenticated producer identity, signed attestation (e.g., JWT with solver license metadata), or protected ledger assertion. Verifier must have a trust root; semantic validation cannot distinguish real execution from fabrication.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
