---
name: crossprovider hermes lease-lock-model-must-include-acquire-atomicity-
description: Lease/lock model must include: acquire atomicity, owner, heartbeat, expiry, recovery
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [scheduler-reliability, duplicate-prevention, distributed-locking]
---

Duplicate-dispatch risk remains high with underspecified leases. Safe lease semantics require: atomic acquire with owner identity, heartbeat/renewal tracking, stale-lease expiry timeout, orphaned-lease recovery, and conflict resolution between overlapping scopes. Without these, 'no active lease' looks safe while work is actually active elsewhere.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
