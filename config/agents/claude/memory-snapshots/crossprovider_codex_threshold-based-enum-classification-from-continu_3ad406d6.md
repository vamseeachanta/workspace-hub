---
name: crossprovider codex threshold-based-enum-classification-from-continu
description: Threshold-based enum classification from continuous values
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [enum-pattern, classification, data-models]
---

Use tuples of (threshold, enum_value) pairs sorted ascending to classify continuous metrics into discrete categories; iterate thresholds and return first match, or default to the final enum if all thresholds exceeded. Avoids nested conditionals and scales cleanly to many bands.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
