---
name: crossprovider hermes document-intelligence-ecosystem-spans-1m-items-w
description: Document intelligence ecosystem spans 1M+ items with fragmented catalogs
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [data-architecture, document-intelligence, workspace-hub-scale]
---

The workspace-hub has indexing infrastructure at scale: 1.3M items across 12 domains, 639K summaries (62% done), standards-transfer-ledger with 425 entries, and 7 separate resource catalogs (catalog.yaml, open-source-engineering-catalog.yaml, web_resources.yaml x3, naval-architecture-resources.yaml, public-og-data-sources.yaml) with overlapping content. Issues #1576–1580 aim to unify these into a single online-resource-registry.yaml + per-domain resource views. Current coverage: OrcaWave, OrcaFlex, naval-architecture, CAD (274K items), pipeline (188K). This unification is load-bearing for cross-domain resource discovery.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
