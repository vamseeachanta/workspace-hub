---
name: crossprovider codex data-provenance-unknown-is-a-safety-gate-never-a
description: Data provenance 'unknown' is a safety gate; never attach inferred meanings
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-integrity, definitions, safety]
---

In definition files and data catalogs, rows marked `provenance: unknown` must never have a `label` or meaning attached, even via fallback/legacy fields. Invented meanings propagate silently into downstream published outputs (NPVs, summaries). Maintain a strict rule: `label: null` when provenance is unknown.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
