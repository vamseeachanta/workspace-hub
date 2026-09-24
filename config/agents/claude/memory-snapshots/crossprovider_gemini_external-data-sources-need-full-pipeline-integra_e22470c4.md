---
name: crossprovider gemini external-data-sources-need-full-pipeline-integra
description: External data sources need full pipeline integration, not filesystem-only drops
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [data-pipeline, integration, registry, sources]
---

Newly available collections from mounted paths (e.g., `/mnt/ace/mkt-a-codes`) must be: inventoried, classified, registered in canonical registries (mounted-source-registry, standards-transfer-ledger), deduplicated against existing corpus, and integrated into existing indexing pipelines. Leaving them as filesystem-only drops forfeits ecosystem discoverability, deduplication, and reusability.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
