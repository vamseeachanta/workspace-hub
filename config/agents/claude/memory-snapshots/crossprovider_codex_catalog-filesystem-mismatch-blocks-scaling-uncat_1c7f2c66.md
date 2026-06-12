---
name: crossprovider codex catalog-filesystem-mismatch-blocks-scaling-uncat
description: Catalog-filesystem mismatch blocks scaling — uncataloged dirs must not be ingested
metadata:
  type: reference
  source: codex
  bridged: 2026-05-27
  tags: [source-inventory, catalog-discrepancy, scaling-blocker]
---

Claimed /mnt/ace/O&G-Standards is ~54K docs/43 GB; actual `_catalog.json` reports 27,343 docs/6.4 GB. Top-level dirs ABS, ASCE, ASME, AWS, NACE are not in catalog. Do not plan bulk ingest from uncataloged dirs; catalog/inventory reconciliation is blocking dependency.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
