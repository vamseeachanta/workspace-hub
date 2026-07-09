---
name: crossprovider codex evidence-validation-must-enforce-shape-contracts
description: Evidence validation must enforce shape contracts, not accept magic strings
metadata:
  type: reference
  source: codex
  bridged: 2026-07-04
  tags: [security, evidence-validation, contract-enforcement]
---

Accepting `durable_output_gate_evidence='issue_61_verified'` or `validator_exit_status=0` as literal flags is forgeable. Evidence must match a required shape (e.g., the #63 contract requires `canary_command`, `exit_code`, `scanned_paths`, `contract_version`, `timestamp_utc`). Minimal self-asserted evidence bypasses the whole point of having a certification contract.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
