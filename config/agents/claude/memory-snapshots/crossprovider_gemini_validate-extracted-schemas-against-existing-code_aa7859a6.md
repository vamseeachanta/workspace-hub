---
name: crossprovider gemini validate-extracted-schemas-against-existing-code
description: Validate extracted schemas against existing code modules
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [data-design, extraction, validation]
---

When designing an extraction schema, create an alignment table mapping extracted fields to existing module structures (constants, function parameters, data classes). Ensures extracted data integrates without incompatibility; prevents inventing new schema structures that diverge from the codebase.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
