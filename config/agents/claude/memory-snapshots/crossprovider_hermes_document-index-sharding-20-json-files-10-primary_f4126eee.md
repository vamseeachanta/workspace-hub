---
name: crossprovider hermes document-index-sharding-20-json-files-10-primary
description: Document index sharding: 20 JSON files (10 primary + 10 ace-overflow shards)
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [data-architecture, sharding, incremental-processing]
---

1.3M documents split across shard-00..09 (workspace-hub) + ace-shard-00..09 (overflow from /mnt/ace). 390K lines total JSON, each shard ~20K entries. Checkpoints/ directory has YAML progress snapshots (dates 2026-03-14 to 2026-03-24), logs/ has 64 Claude worker logs (shard-by-shard processing). This sharding strategy enables parallel processing and incremental updates without reprocessing entire index.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
