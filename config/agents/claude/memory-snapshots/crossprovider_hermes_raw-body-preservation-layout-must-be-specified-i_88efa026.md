---
name: crossprovider hermes raw-body-preservation-layout-must-be-specified-i
description: Raw-body preservation layout must be specified in producer/consumer contract
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [artifact-format, producer-contract, consumer-parsing]
---

Whether diagnostics/errors live in metadata vs. body, and where raw output lands relative to headers (immediately after blank line vs. elsewhere), must be pinned in the contract. Otherwise tests assert layout that the producer doesn't guarantee and producer outputs layout that consumer doesn't parse. Conflict found in #2502 producer pseudocode.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
