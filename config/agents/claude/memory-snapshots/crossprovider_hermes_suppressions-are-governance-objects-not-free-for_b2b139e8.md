---
name: crossprovider hermes suppressions-are-governance-objects-not-free-for
description: Suppressions are governance objects, not free-form exceptions
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [governance, schema, suppression]
---

Unresolved-read suppressions must be executable schema objects with owner, expires_at, reviewer fields. Expired or unreviewed waivers should fail the weekly regression gate they are meant to bypass; this enforces waiver lifecycle and prevents suppressions from becoming stale technical debt.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
