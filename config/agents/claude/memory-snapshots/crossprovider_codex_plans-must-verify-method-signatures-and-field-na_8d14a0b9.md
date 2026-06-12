---
name: crossprovider codex plans-must-verify-method-signatures-and-field-na
description: Plans must verify method signatures and field names in live code, not assume them
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [plan-rigor, source-verification, api-contracts]
---

Codex reviews found multiple plans assuming API shapes (fetch(ticker) → pd.DataFrame, tool_name field names in event logs, YAML enum values) without reading the actual source. Every method invocation and schema assumption must cite a specific file:line from the repository. Abstract claims like 'the validator checks are straightforward' are unacceptable without evidence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
