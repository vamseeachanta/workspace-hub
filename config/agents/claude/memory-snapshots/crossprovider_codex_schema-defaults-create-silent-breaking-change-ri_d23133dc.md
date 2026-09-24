---
name: crossprovider codex schema-defaults-create-silent-breaking-change-ri
description: Schema defaults create silent breaking-change risk
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema, breaking-changes, compatibility]
---

Making type='auto' conversion-fatal breaks existing code using the default value. Changes affecting fields with schema defaults require explicit migration paths, not just behavioral changes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
