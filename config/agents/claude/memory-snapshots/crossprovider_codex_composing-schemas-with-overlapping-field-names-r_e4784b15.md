---
name: crossprovider codex composing-schemas-with-overlapping-field-names-r
description: Composing schemas with overlapping field names requires explicit deconfliction and wrapper patterns
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [schema-design, composition, architectural-pattern]
---

When integrating multiple schema definitions that share field names with different semantics, rename one explicitly to prevent data loss or misinterpretation. For closed schemas (additionalProperties: false), new fields must go in a wrapper field at a parent level, not inline.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
