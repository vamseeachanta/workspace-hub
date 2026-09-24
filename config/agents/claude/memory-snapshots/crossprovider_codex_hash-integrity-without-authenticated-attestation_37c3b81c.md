---
name: crossprovider codex hash-integrity-without-authenticated-attestation
description: Hash integrity without authenticated attestation cannot prevent fabrication
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, attestation, trust-model]
---

Semantic checks and result hashing cannot distinguish fabricated results from licensed solver execution without authenticated producer identity, signed attestation, protected ledger, or verifier trust root. Integrity requires cryptographic binding to the producer, not just internal consistency of hashes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
