---
name: crossprovider codex enum-reuse-across-contexts-creates-logical-incon
description: Enum reuse across contexts creates logical inconsistency
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [schema-design, naming, validation]
---

Using 'rejected' as both control-plane verification state and page-shape parse status makes tests logically inconsistent (must accept and reject the same bare string). Rename one value or add context-qualified field names.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
