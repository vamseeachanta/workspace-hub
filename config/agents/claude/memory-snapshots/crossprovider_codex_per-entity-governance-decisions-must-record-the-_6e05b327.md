---
name: crossprovider codex per-entity-governance-decisions-must-record-the-
description: Per-entity governance decisions must record the entity identifier
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [schema-design, governance, downstream-contracts]
---

When a schema requires "per-root applicability decisions," the output must include `opaque_root_id` or equivalent so downstream consumers know which entities each decision applies to. Class-level aggregation alone leaves downstream work re-identifying eligible/blocked entities. Observed in llm-wiki #729 — emitted class-level rows without opaque_root_id, blocking #730/#734's decision-making.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
