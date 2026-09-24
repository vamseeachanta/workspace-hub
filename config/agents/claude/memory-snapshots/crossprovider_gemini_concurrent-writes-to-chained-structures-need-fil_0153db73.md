---
name: crossprovider gemini concurrent-writes-to-chained-structures-need-fil
description: Concurrent writes to chained structures need file locking
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [concurrency, locks, audit-trail, bash]
---

SHA256-chained audit logs and similar sequential structures break under concurrent write without synchronization. Use flock or equivalent to prevent race conditions where the 'previous hash' is read before another process finishes writing it.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
