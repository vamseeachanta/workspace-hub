---
id: ADR-005
type: decision
title: "Resource-intelligence schema for document-sourced knowledge"
category: architecture
tags: [knowledge-management, resource-intelligence, schema, document-extraction]
repos: [workspace-hub]
confidence: 0.9
created: "2026-03-25"
last_validated: "2026-03-25"
source_type: session
related: [ADR-002, ADR-004]
status: active
access_count: 0
---

# Resource-Intelligence Schema for Document-Sourced Knowledge

## Context

The workspace-hub knowledge system has two layers: structured entries in `.claude/knowledge/` (11 entries across ADR, GOT, PAT, TIP types) and a flat KNOWLEDGE.md file (96 lines of institutional memory). Both capture knowledge that originates from *within* the project -- decisions made, patterns discovered, gotchas encountered.

There is no structured way to capture knowledge extracted *from external sources*: standards (DNV-RP-C203, API-RP-2A), software documentation (OrcaFlex, AQWA), data files (vessel RAOs, environmental data), or technical papers. When an agent session parses a PDF, reads a standard, or analyzes a dataset, the resulting insights end up as ephemeral summaries in MEMORY.md. These summaries lack source traceability, confidence levels, staleness tracking, and domain context. They cannot be queried, validated, or reused across sessions.

The existing index.json pattern works well for project-internal knowledge but needs a new entry type for document-sourced intelligence.

## Decision

Introduce a `resource` entry type with prefix `RES-NNN`, stored in `.claude/knowledge/entries/resources/` and indexed in the existing `index.json`. The schema is defined in `.planning/architecture/resource-intelligence-schema.yaml`.

Key design choices:

1. **Five entry sub-types** (`entry_type` field): `finding`, `datapoint`, `procedure`, `reference`, `lesson` -- covering the range from specific numeric values to methodological lessons learned.

2. **Source metadata block** with `name`, `source_kind`, `url`, `file_path`, `page`, `section`, `edition`, `retrieved` -- enough to trace back to the exact location in the original document.

3. **Provenance chain** with `method` (manual, doc-intelligence, agent-session, hybrid), optional `session_id`, `agent_model`, `reviewed_by`, and `review_date` -- distinguishing human-authored from agent-extracted entries and tracking review status.

4. **Domain tagging** with `primary` domain and optional `sub_domain` -- enabling domain-scoped queries (e.g., "all fatigue knowledge", "all hydrodynamics datapoints").

5. **Staleness via TTL** (`ttl_days`) rather than fixed expiry dates -- standards change slowly (365-730 days), tool documentation changes faster (90-180 days), project data drifts quickly (30-90 days).

6. **Usage tracking** with `access_count` and `last_accessed` -- identifying high-value entries and detecting unused ones for cleanup.

7. **Full index.json compatibility** -- RES entries use the same top-level fields (`id`, `type`, `title`, `category`, `tags`, `repos`, `confidence`, `created`, `last_validated`, `related`, `status`, `access_count`, `file`). The `source_type` field in the index maps from `provenance.method`.

## Consequences

### Positive

- Document-sourced knowledge becomes durable and queryable instead of ephemeral.
- Source traceability means entries can be revalidated when standards are updated.
- Domain tagging enables scoped retrieval (agent asks "what do we know about fatigue?").
- Provenance tracking distinguishes verified human knowledge from unreviewed agent extractions.
- TTL-based staleness replaces manual "stale:" annotations currently used in KNOWLEDGE.md.
- Flat-file YAML/Markdown storage requires no new tooling -- same git-based workflow.

### Negative

- Adds a fifth entry directory and type to the knowledge system -- marginally more complexity.
- Agent-extracted entries at low confidence require a human review workflow that does not yet exist.
- TTL checking needs a script or hook to flag stale entries (not yet implemented).

## Migration Path

1. **Create directory**: `.claude/knowledge/entries/resources/`
2. **Backfill from KNOWLEDGE.md**: Entries in the "Tool/Solver Quick Reference" and "Debugging Protocol" sections that cite specific external sources (OrcaWave API, AQWA manual, DNV standards) are candidates for RES entries. Migrate incrementally -- do not bulk-convert.
3. **Update index rebuild script**: If one exists, add `resource` to the type discovery list and `RES-` to the ID pattern.
4. **Add TTL check**: A future script in `scripts/` can scan `index.json` for entries where `today - last_validated > ttl_days` and emit warnings.
5. **Future: SQLite migration**: The schema uses JSON Schema-compatible types. If the entry count exceeds ~200, a SQLite store with the same columns is a straightforward migration. The YAML schema documents the contract.

## References

- Schema: `.planning/architecture/resource-intelligence-schema.yaml`
- Existing index: `.claude/knowledge/index.json`
- Knowledge format ADR: ADR-002
- Data residence strategy: ADR-004
- Issue: workspace-hub #894
