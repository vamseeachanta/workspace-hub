---
name: crossprovider codex checkpoint-counters-alone-cannot-verify-ledger-i
description: Checkpoint counters alone cannot verify ledger integrity
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [ledger-integrity, restart-safety, reconciliation]
---

A completed ledger that trusts stored checkpoint values on restart without recounting actual inventory_records rows cannot detect row deletion, duplication, or tampering. On every completed restart, independently query actual row count, distinct PK count, sequence/checkpoint consistency, and canary digest; fail closed on any mismatch.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
