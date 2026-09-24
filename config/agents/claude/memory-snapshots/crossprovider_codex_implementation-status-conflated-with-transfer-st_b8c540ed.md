---
name: crossprovider codex implementation-status-conflated-with-transfer-st
description: Implementation status conflated with transfer status in schema
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema-design, semantic-overload, state-model]
---

Legacy `done` field derived from upstream `implemented` state or completed work items gets mislabeled as 'transfer history' in schema redesigns. Downstream consumers (query-ledger, generate-coverage-report) interpret it as availability/acquisition state. Requires explicit workflow classification (implementation vs transfer vs availability) per field to prevent misuse.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
