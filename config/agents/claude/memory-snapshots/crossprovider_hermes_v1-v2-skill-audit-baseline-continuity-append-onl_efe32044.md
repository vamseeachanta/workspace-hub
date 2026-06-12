---
name: crossprovider hermes v1-v2-skill-audit-baseline-continuity-append-onl
description: v1→v2 skill audit baseline continuity: append-only compatibility required
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [audit-versioning, baseline-continuity, schema-evolution]
---

When migrating v1 audit findings to v2 schema, prior v1 findings must not all become falsely 'new' on first v2 run; declare append-only compatibility and preserve baseline keys/schema so delta is checkable.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
