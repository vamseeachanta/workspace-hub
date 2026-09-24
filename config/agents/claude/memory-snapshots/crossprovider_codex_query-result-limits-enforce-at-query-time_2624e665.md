---
name: crossprovider codex query-result-limits-enforce-at-query-time
description: Query result limits: enforce at query time
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [database, sql, performance, safety]
---

Canary/sampling queries should enforce result caps via LIMIT clause at query time, not after `fetchall()`. Post-fetch cap checks defeat bounded-pilot safety semantics and risk full-corpus materialization in memory before the cap is detected.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
