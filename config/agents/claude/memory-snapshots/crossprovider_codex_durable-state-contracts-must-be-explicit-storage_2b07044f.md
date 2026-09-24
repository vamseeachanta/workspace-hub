---
name: crossprovider codex durable-state-contracts-must-be-explicit-storage
description: Durable state contracts must be explicit — storage, keying, deduplication
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [state-management, contract-specificity, analytics]
---

Accepting a requirement like "track 30-day rolling trends" without defining where state lives, how sessions are keyed by date, how duplicates are avoided, or what artifact gets updated will lead to incomplete implementations. State contracts must include location, schema, and lifecycle.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
