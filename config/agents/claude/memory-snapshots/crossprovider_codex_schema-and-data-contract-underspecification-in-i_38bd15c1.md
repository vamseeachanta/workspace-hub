---
name: crossprovider codex schema-and-data-contract-underspecification-in-i
description: Schema and data-contract underspecification in infrastructure plans
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [adversarial-review, infrastructure, schema-design, data-contracts]
---

Multiple plan reviews flagged fragmented ownership of data schemas: input shape vs. output shape confusion, field mapping without formulas, report schema/writer/parser split across sections with no concrete module binding. Infrastructure plans need a dedicated 'Data Contracts' section that names the actual source/sink modules (Python classes, files, CLI outputs) with their I/O shapes and field semantics.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
