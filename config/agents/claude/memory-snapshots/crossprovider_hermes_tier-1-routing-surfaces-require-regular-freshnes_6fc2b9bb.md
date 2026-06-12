---
name: crossprovider hermes tier-1-routing-surfaces-require-regular-freshnes
description: Tier-1 routing surfaces require regular freshness audits for drift
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [routing-surfaces, indexing, drift-detection]
---

AGENTS.md, README.md, docs/README.md, operator maps, and registry references in workspace-hub and sub-repos should be audited ~daily for broken links, missing files, stale registries, and cache/runtime noise. A drift in tier-1 surfaces weakens future issue routing and code placement. Refresh a local report and track status: green/yellow/red per repo.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
