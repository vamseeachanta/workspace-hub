---
name: crossprovider codex quota-provider-status-rate-limited-quota-exceede
description: Quota provider status (rate-limited/quota-exceeded) is hard gate failure
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [gates, quota-management, provider-health]
---

When provider reports unavailability in quota_snapshot.status, treat as gate failure (False), not warning. Blocks workflow progression until quota recovers. Indicates provider health state is load-bearing for work authorization.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
