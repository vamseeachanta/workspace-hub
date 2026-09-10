---
name: crossprovider codex heartbeat-identity-renames-create-transient-dead
description: Heartbeat/identity renames create transient dead-host windows
metadata:
  type: reference
  source: codex
  bridged: 2026-07-31
  tags: [migrations, identity, transition-windows]
---

When renaming long-lived artifacts (heartbeat files, routing tokens), a migration period creates ambiguity: old names read as dead/missing before new names settle. The alarm layer cannot distinguish a renamed host from a truly offline one. Rename migrations must include explicit mapping and cannot land during blind-spot periods.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
