---
name: crossprovider hermes tier-1-indexing-freshness-audit-detects-routing-
description: Tier-1 indexing freshness audit detects routing-adjacent drift daily
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [indexing, drift-detection, routing-stability]
---

Daily cron `tier1-indexing-freshness.sh` audits canonical surfaces (AGENTS.md, docs/README.md, operator maps). Material drift = runtime/log artifacts in trusted-adjacent paths (docs/plans/, docs/reports/). When detected, routing trust model weakens. Emerging monitoring pattern.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
