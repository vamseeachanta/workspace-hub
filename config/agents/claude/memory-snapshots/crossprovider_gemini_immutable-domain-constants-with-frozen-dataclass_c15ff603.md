---
name: crossprovider gemini immutable-domain-constants-with-frozen-dataclass
description: Immutable domain constants with frozen dataclasses
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [pattern-immutable-constants, dataclasses, standards-traceability]
---

User employs `@dataclasses.dataclass(frozen=True)` for immutable domain constants (steel grades, material properties) with explicit reference/standard metadata. This pattern prevents accidental mutation and maintains traceability to source standards (API 5L, ASTM, etc.).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
