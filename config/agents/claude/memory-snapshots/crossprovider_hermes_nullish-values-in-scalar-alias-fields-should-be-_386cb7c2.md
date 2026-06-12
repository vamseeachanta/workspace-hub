---
name: crossprovider hermes nullish-values-in-scalar-alias-fields-should-be-
description: Nullish values in scalar alias fields should be treated as absent
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [llm-wiki, yaml-parsing, data-quality]
---

YAML scalar values `None`, `null`, `~`, and empty strings in alias/supersedes fields are being committed to artifacts as real edges (e.g., `external:None`). These should be filtered out during generation or explicitly rejected by schema validation. Test for all nullish variants.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
