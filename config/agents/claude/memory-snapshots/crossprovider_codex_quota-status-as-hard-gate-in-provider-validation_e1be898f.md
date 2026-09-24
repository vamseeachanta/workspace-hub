---
name: crossprovider codex quota-status-as-hard-gate-in-provider-validation
description: Quota status as hard gate in provider validation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [provider-operations, gates, quota-management]
---

Treat provider quota exhaustion (`quota_snapshot.status` in rate-limited or quota-exceeded state) as hard gate failures in orchestration checks, not degradations. This prevents silently accepting work when providers are unavailable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
