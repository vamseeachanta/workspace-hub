---
name: crossprovider codex contract-files-can-assert-rules-without-validato
description: Contract files can assert rules without validators actually enforcing them
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, contracts, test-coverage, negative-cases]
---

A JSON contract can list a required field or enum constraint, but the validator code may only check the contract's internal consistency, not validate inbound records against the constraint. Negative test fixtures are needed to expose this gap. When reviewing implementations, run probe cases that should be rejected by the stated contract.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
