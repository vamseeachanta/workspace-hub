---
name: crossprovider codex distinguish-caption-inventory-from-extracted-tab
description: Distinguish caption inventory from extracted table data in schema
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [ingest, tables, schema, artifacts]
---

A CSV listing found-table counts and captions is structurally different from extracted table data (actual rows/values). Use separate schema fields and status values; don't conflate caption-inventory-only with table-extraction-complete.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
