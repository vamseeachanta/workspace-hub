---
name: crossprovider gemini schema-assumptions-must-be-verified-against-sour
description: Schema assumptions must be verified against source code, not sample files
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [plan-review, correctness, schema]
---

Plans that infer JSON/YAML schema from log samples risk runtime failures when schema changes. Always retrieve and cite the actual source code (logger implementation, config parser, API docs) to verify field names, types, and presence guarantees before pseudocode is written.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
