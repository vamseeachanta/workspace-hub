---
name: crossprovider hermes data-migration-first-blocks-execution-until-clas
description: Data migration-first blocks execution until classification completes
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [data-migration, inventory, execution-blocking]
---

When data has been piecemeal-moved across repos/locations (e.g. llm-wiki raw ↔ public separation in #2726), treat as migration/inventory-first, not greenfield. Execution layers should use abstract identifiers (source_id, source_registry_kind, input/output_residency) and fail closed on ambiguous paths until data is classified and canonical locations are established. Blocks must persist until #NNNN inventory issues close.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
