---
name: crossprovider hermes degraded-observability-failures-are-the-most-lik
description: Degraded-observability failures are the most likely control-plane failure mode
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [scheduler-reliability, observability, failure-modes]
---

When ledger is missing/untrusted, PR association is weak, or comment retrieval is partial, the classifier can look correct (clean markers, valid review) while being incomplete (unaware of already-active work). Missing observability is not an acceptable hazard even with best-effort warnings. Degrade recommendations, not safety.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
