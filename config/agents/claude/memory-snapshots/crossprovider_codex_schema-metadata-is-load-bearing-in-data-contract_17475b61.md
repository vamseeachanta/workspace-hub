---
name: crossprovider codex schema-metadata-is-load-bearing-in-data-contract
description: Schema metadata is load-bearing in data contracts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema-design, data-contracts, planning-rigor]
---

Data model specifications often omit metadata fields that enable downstream operations (comparison, interpolation, conversion). When defining a schema, enumerate all fields needed by all planned operations, not just primary payload. Example: excitation models need phase_convention and unit_system for comparison, not just amplitude/phase.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
