---
name: crossprovider gemini pseudocode-must-explicitly-define-all-variables-
description: Pseudocode must explicitly define all variables; implicit definitions hide runtime errors
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [pseudocode, code-quality, variable-scope]
---

Plans with pseudocode that uses undefined variables (e.g., `$today` not derived from `utcnow()`) will fail at runtime with unclear errors. Every variable reference must have a clear assignment line before use. TDD tests should catch these, but test cases themselves often misspecify the expected structure.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
