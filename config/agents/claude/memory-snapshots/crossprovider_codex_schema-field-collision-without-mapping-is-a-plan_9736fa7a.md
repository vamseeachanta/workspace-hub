---
name: crossprovider codex schema-field-collision-without-mapping-is-a-plan
description: Schema field collision without mapping is a plan blocker
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema-design, plan-review, governance]
---

When a plan introduces a new enum on an existing schema field name (e.g., new `source_class` values on a field that already has different enums), the plan becomes unimplementable until explicit field mapping, renaming, or layering rules are added. Acknowledging that schemas exist is not the same as reconciling field collisions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
