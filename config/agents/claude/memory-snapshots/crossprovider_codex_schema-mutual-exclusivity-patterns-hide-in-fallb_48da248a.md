---
name: crossprovider codex schema-mutual-exclusivity-patterns-hide-in-fallb
description: Schema mutual-exclusivity patterns hide in fallback logic
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema, validation, fallback-logic]
---

When a schema forbids certain states (e.g., vessel XOR bodies in DiffractionSpec), plans that assume fallback chains across those forbidden states will fail at runtime. Enumerate the actual valid spec states before designing multi-level fallback chains. Example: #609 assumed spec.vessel.control_surface exists in multi-body mode, but the schema forbids bodies and vessel together.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
