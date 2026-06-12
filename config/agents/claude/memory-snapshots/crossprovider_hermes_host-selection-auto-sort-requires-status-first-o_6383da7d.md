---
name: crossprovider hermes host-selection-auto-sort-requires-status-first-o
description: Host selection auto-sort requires status-first ordering
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [dispatch, host-selection, ordering]
---

Auto-host-selector enumerated hosts without sorting by readiness status first, allowing 'warn' hosts to be selected before 'pass' hosts. Selection must sort statuses before choosing.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
