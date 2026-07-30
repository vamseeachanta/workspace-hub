---
name: crossprovider codex validator-class-membership-is-the-enforcement-bo
description: Validator class membership is the enforcement boundary in registry systems
metadata:
  type: reference
  source: codex
  bridged: 2026-07-08
  tags: [architecture, source-policy, schema-design]
---

In a registry with approved source classes, the validator's class list determines what can drive conversions. URLs assigned to non-conversion classes can coexist with `accepted_for_conversion: false` without elevation; checking class membership prevents policy violations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
