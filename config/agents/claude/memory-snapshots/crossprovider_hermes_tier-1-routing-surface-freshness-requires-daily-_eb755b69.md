---
name: crossprovider hermes tier-1-routing-surface-freshness-requires-daily-
description: Tier-1 routing surface freshness requires daily canonical monitoring
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [maintenance, routing-surfaces, freshness-audit]
---

Recurring cron audits AGENTS.md, README.md, docs/README.md, and repo operator maps for broken references, missing surfaces, stale registry data, and workspace cruft. Report refreshes timestamp even if no drift detected. Detects noise that weakens routing trust across tier-1 repos.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
