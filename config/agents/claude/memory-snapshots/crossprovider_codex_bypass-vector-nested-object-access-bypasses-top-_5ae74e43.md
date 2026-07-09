---
name: crossprovider codex bypass-vector-nested-object-access-bypasses-top-
description: Bypass vector: nested object access bypasses top-level validator guards
metadata:
  type: reference
  source: codex
  bridged: 2026-07-02
  tags: [validator-completeness, bypass, data-model]
---

Validators that block `route_targets` at top level but accept the same forbidden enum inside a nested object create a bypass. Schema validators need to walk all object paths or use a path-agnostic rule checker.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
