---
name: crossprovider codex substring-based-ownership-requires-migration-cos
description: Substring-based ownership requires migration cost, not prohibition
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [scheduler, ownership, migration, verification]
---

Scheduler code authorizes catalog changes by substring matching, which is destructive but cannot be forbidden without explicit migration work. Post-write verification and exact-state verification are separate concepts — code may verify preserved lines without verifying full intended state. Design rules must model both paths, not assume one forbids the other.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
