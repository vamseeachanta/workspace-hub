---
name: crossprovider hermes tier-1-routing-surfaces-need-daily-audit
description: Tier-1 routing surfaces need daily audit
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [tier-1-routing, curation, index-freshness]
---

Canonical routing surfaces (AGENTS.md, README.md, docs/README.md, docs/maps/*-operator-map.md, docs/registry/*-routing.yaml) must be current so code placement and retrieval work reliably. Cron daily to detect drift: broken links, missing docs/README, missing operator maps, stale registries, root/index noise. Report per-repo status (green/yellow/red); refresh even if no drift (timestamp proof).

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
