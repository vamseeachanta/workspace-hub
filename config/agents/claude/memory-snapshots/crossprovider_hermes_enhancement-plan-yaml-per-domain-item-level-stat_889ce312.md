---
name: crossprovider hermes enhancement-plan-yaml-per-domain-item-level-stat
description: Enhancement-plan.yaml: per-domain item-level status tracking for 1M+ documents
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [document-index, domain-tracking, work-prioritization]
---

34K-line YAML tracking 1.3M items across 12 domains (other 176K, cad 475K, portfolio 55K, pipeline 187K, etc). Structure: by_domain → domain → items[] with fields (doc_number, title, path, status, notes). Used to identify gaps (status=gap) and guide enhancement prioritization. Generated 2026-03-15, last updated programmatically. When working on domain-specific projects, query this ledger to understand what's already indexed vs missing.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
