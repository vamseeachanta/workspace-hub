---
name: crossprovider codex sandbox-write-permission-boundaries-may-not-matc
description: Sandbox write-permission boundaries may not match stated scope
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [sandbox, permissions, operations]
---

Declared 'workspace-write' scope (/mnt paths) may not be actually writable in sandbox. Write failures block corrective passes and cannot be recovered in-session. Always verify actual writable roots before committing to fix strategy.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
