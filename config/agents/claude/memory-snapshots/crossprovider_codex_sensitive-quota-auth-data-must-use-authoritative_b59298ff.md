---
name: crossprovider codex sensitive-quota-auth-data-must-use-authoritative
description: Sensitive quota/auth data must use authoritative sources only, never estimates
metadata:
  type: reference
  source: codex
  bridged: 2026-06-17
  tags: [security, quota-management, authentication]
---

For quota, rate-limits, and authentication state, use authoritative sources (OAuth snapshots, API live queries) exclusively—never local caches or estimates as fallback. Fail-closed with explicit NAs/unavailable status rather than guessing stale values.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
