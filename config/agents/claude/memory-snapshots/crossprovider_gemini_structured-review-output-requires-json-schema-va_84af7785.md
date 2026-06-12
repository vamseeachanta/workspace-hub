---
name: crossprovider gemini structured-review-output-requires-json-schema-va
description: Structured review output requires JSON schema validation
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [validation, review-harness, schema-design]
---

Cross-review harness enforces schema with required fields: verdict, summary, issues_found, suggestions, questions_for_author. Schema prevents malformed outputs from downstream processors.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
