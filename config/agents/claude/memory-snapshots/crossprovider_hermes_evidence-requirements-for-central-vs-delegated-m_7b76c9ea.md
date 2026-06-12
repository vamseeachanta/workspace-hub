---
name: crossprovider hermes evidence-requirements-for-central-vs-delegated-m
description: Evidence requirements for central-vs-delegated mode selection
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [execution-decision, delegation-criteria, central-execution, evidence]
---

Central vs delegated execution mode selection requires explicit evidence to justify delegation: exact slices, owned/read-only/forbidden path maps, validators, GitHub posting ownership split, and integration/final-verification owner. If this evidence cannot be stated clearly, do not delegate—stay central. This gate happens after entry-condition and already-done pre-check, but before any code changes or prompt packing.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
