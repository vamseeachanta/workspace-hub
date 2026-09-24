---
name: crossprovider codex storage-exhaustion-is-an-operational-blocker-not
description: Storage exhaustion is an operational blocker, not a test edge case
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [storage, operational-constraints, multi-agent]
---

When filesystem free space drops below ~10 MB (especially on shared FUSE-mounted storage), write attempts fail before the file is created, leaving zero-byte artifacts. This is not pathological; it's a real constraint in multi-user/multi-agent environments. Session scratch cleanup is operational necessity, not optional housekeeping.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
