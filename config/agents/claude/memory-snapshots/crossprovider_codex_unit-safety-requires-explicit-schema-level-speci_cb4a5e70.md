---
name: crossprovider codex unit-safety-requires-explicit-schema-level-speci
description: Unit safety requires explicit schema-level specification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema-design, api-clarity, data-integrity]
---

Deduplication and APIs that accept numeric values must explicitly specify units in dataclass fields, CSV column headers, and all downstream schemas—not just in human-readable documentation. Implicit units allow silent merging of distinct engineering values (e.g., weight in pounds vs kilograms). Define typed equivalence rules with units baked in.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
