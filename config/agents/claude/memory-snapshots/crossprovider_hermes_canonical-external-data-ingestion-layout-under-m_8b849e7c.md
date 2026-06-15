---
name: crossprovider hermes canonical-external-data-ingestion-layout-under-m
description: Canonical external data ingestion layout under /mnt/ace/<repo-name>/
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [data-management, storage-layout, external-drives]
---

External drives ingest to `/mnt/ace/<repo-name>/<domain>/` with repo-aligned buckets (lng-a, digitalmodel, achantas-data, acma-codes). Ask disposition questions upfront before file operations to avoid rework and naming conflicts with existing structures.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
