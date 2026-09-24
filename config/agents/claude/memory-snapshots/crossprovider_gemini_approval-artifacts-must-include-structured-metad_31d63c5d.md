---
name: crossprovider gemini approval-artifacts-must-include-structured-metad
description: Approval artifacts must include structured metadata for auditability
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [approval, auditability, metadata, governance]
---

Track approver ID, ISO 8601 timestamp, and status enum (APPROVED_FOR_DRYRUN/SIMULATION/APPROVED) in artifact headers. Enables audit trail and prevents ambiguous approval state. Compute SHA256 digest of approval artifacts for immutability.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
