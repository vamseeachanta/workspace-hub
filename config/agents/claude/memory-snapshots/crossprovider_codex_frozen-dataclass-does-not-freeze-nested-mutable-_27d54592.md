---
name: crossprovider codex frozen-dataclass-does-not-freeze-nested-mutable-
description: Frozen dataclass does not freeze nested mutable containers
metadata:
  type: reference
  source: codex
  bridged: 2026-07-06
  tags: [python-pitfall, immutability, validation]
---

Python `@dataclass(frozen=True)` only freezes top-level attributes. Nested dicts, lists, and other mutable objects inside a frozen dataclass can still be mutated or bypassed via public constructor calls. Use immutable types (tuple, frozenset, MappingProxyType) or property-based access control to enforce invariants.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
