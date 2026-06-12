---
name: crossprovider hermes evidence-refresh-as-alternative-to-relaunch
description: Evidence refresh as alternative to relaunch
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [monitoring, blocked-operations, cost-efficiency, evidence-artifacts]
---

When blocked on governance gates, refresh monitoring evidence (live GitHub issue state, process scans, branch SHAs, log tails, secret scans) rather than re-launching bundles. Evidence refresh costs < re-launch, produces actionable blocker documentation for decision-maker, and avoids wasted resource spend. Pattern observed across 10+ monitoring cycles on same blocked bundles.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
