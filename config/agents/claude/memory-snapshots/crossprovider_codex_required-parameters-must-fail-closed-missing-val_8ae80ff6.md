---
name: crossprovider codex required-parameters-must-fail-closed-missing-val
description: Required parameters must fail closed; missing values should never degrade to empty/default
metadata:
  type: reference
  source: codex
  bridged: 2026-07-10
  tags: [validation, error-handling, fail-closed]
---

Empty strings passing through as valid values for required predicates (state, county) let invalid requests masquerade as no-match searches. Validation must enforce presence and non-empty for required parameters, not allow-if-present. Distinguish 'missing parameter' (error) from 'valid parameter, no match' (success).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
