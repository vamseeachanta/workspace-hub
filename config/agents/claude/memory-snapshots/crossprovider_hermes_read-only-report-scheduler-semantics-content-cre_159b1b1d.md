---
name: crossprovider hermes read-only-report-scheduler-semantics-content-cre
description: Read-only report + scheduler-semantics content = creeping authority
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [scope-creep, reporting, scheduler-vs-report]
---

Reports/classifiers that claim to be read-only observation but include dispatch state machines, lease lifecycle, and scheduler policy tend to become operationally authoritative even when not intended. Downstream operators treat them as truth rather than advisory. Scope v1 strictly: no scheduler concepts, no dispatch-ledger writes, no state-transition semantics. Save those for explicit follow-up issues.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
