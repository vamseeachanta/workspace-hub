---
name: crossprovider codex enum-based-taxonomies-with-keyword-regex-mapping
description: Enum-based taxonomies with keyword regex mapping for unstructured classification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [classification, taxonomy, pattern-matching]
---

When mapping unstructured strings to domain categories (e.g., incident phases, root causes), use Enum classes with docstrings referencing governing standards. Pair with a keyword map (list of (pattern, enum_value) tuples) using case-insensitive regex for robust matching. Document standard alignment in enum docstrings.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
