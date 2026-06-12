---
name: crossprovider codex numeric-snapshots-in-plans-create-brittleness
description: Numeric snapshots in plans create brittleness
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [planning, acceptance-criteria, versioning]
---

Plans should avoid static snapshot values (e.g., 'after this change, count will be 24'). Instead, encode dynamic rules (e.g., 'count at write-time + 1') and use snapshots only for baseline validation. Static values block plan re-evaluation without becoming stale.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
