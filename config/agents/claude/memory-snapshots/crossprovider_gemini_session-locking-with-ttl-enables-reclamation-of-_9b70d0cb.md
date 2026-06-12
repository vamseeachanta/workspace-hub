---
name: crossprovider gemini session-locking-with-ttl-enables-reclamation-of-
description: Session locking with TTL enables reclamation of stale locks
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [session-management, locking, TTL, WRK-157, WRK-158]
---

Implement session locks with configurable TTL (default 2 hours). When lock age exceeds TTL, new session can reclaim the item. Separate staleness markers warn at 7 days, critical at 14 days. Enables recovery from crashed sessions without manual intervention.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
