---
name: crossprovider gemini material-grades-frozen-dataclass-flat-public-dic
description: Material grades: frozen dataclass + flat public dict for fast lookup
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [material-properties, registry-pattern, dataclass]
---

Store grades in public dict keyed by name (STEEL_GRADES['X65']) using @dataclass(frozen=True) values. No manager class needed; direct lookups are O(1) and registry is immutable. Optional getter (get_steel_grade) returns None on miss, simplifying error handling.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
