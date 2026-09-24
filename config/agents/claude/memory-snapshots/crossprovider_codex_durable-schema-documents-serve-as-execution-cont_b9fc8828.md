---
name: crossprovider codex durable-schema-documents-serve-as-execution-cont
description: Durable schema documents serve as execution contracts for generators and validators
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema-contract, documentation-driven, generator-validator-alignment]
---

Schema documents (e.g., `docs/schemas/public-graph-v1.md`) define artifact structure, field requirements, allowed relations, and safety rules that both generator and validator must enforce. This becomes the single source of truth for artifact shape and validation criteria, preventing schema drift between generation and validation logic.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
