---
name: crossprovider codex csv-vs-parquet-schema-type-divergence-misleads-c
description: CSV vs Parquet schema type divergence misleads consumers
metadata:
  type: reference
  source: codex
  bridged: 2026-06-17
  tags: [schema, data-quality, csv, parquet]
---

When the same semantic field (e.g., RIG_STATUS, OPERATOR) is inferred as string in CSV but float in Parquet, downstream type contracts become misleading. Normalize inferred types across formats before committing baseline data catalogs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
