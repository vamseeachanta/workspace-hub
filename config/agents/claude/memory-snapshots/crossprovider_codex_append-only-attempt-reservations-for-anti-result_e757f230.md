---
name: crossprovider codex append-only-attempt-reservations-for-anti-result
description: Append-only attempt reservations for anti-result-shopping
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing-patterns, verification, audit-trail]
---

Anti-result-shopping enforcement requires immutable attempt records bound to command/digest/version/invocation details—not just outcome selection. Attempts committed only at result-time can hide partial or repeat executions. Reservation IDs must repeat in outcome records to make the ledger auditable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
