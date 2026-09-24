---
name: crossprovider codex frozen-dataclasses-with-nested-mutable-container
description: Frozen dataclasses with nested mutable containers have a bypass vector
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [python-dataclass, security, design-footgun]
---

`@dataclass(frozen=True)` does not freeze nested dicts/lists. Even with builder-only validation intent, public constructors remain available and can construct objects with mutable maps inside that violate invariants.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
