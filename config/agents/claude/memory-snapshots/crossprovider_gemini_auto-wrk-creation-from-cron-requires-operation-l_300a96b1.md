---
name: crossprovider gemini auto-wrk-creation-from-cron-requires-operation-l
description: Auto-WRK creation from cron requires operation-level locking, not file-level
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [atomicity, cron, auto-generation, concurrency]
---

When scripts auto-create work items (WRK files) from cron, a single flock on state.yaml is insufficient. The entire operation (read next-id, allocate new ID, write new WRK, update state) must be atomic under a comprehensive lock to prevent race conditions if multiple triggers fire simultaneously.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
