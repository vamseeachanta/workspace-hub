---
name: crossprovider gemini add-session-level-locking-for-concurrent-agent-c
description: Add session-level locking for concurrent agent collisions
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [concurrency, workflow-gates, locking]
---

Concurrent AI agent sessions (8+ observed) create WRK-item race conditions: merge conflicts, duplicate work, wasted compute. Implement atomic session-level locks with stale-lock recovery (auto-release >2h), exit code 4 for collision, claim_wrk/release_wrk guards.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
