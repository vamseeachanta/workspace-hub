---
name: crossprovider codex compare-plans-against-origin-main-implementation
description: Compare plans against origin/main implementation, not just stated design assumptions
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [staleness, plan-review, architecture]
---

Plans become stale when new infrastructure ships (e.g., git-ref CAS leases replacing old JSONL leases). Review checklist: always compare the plan's architectural assumptions against current origin/main code, not just re-validate the plan's internal consistency. Flag if the plan references subsystems that have since been superseded or refactored.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
