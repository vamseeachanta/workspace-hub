---
name: crossprovider codex transactional-reconcilers-must-refuse-writes-tha
description: Transactional reconcilers must refuse writes that overwrite uncataloged entries
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [ecosystem-reconciliation, data-integrity]
---

During cross-provider ecosystem reconciliation, a reconciler should reject any write that would lose live entries not yet discovered in the audit. Audit first, map all live state, then reconcile only with boundaries that preserve evidence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
