---
name: crossprovider codex schema-completeness-requires-tooling-verificatio
description: Schema completeness requires tooling verification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-validation, schema-design, tooling-alignment]
---

Schema definitions alone do not capture all enforced values. Cross-reference against actual tooling that produces/validates the data (e.g., index generators, config parsers). Missing values that are enforced by tools = incomplete schema. For category maps: grep the code that generates categories, not just the schema.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
