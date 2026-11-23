---
name: knowledge-source-recon
description: Reconnaissance pattern to inventory all knowledge sources across the workspace-hub ecosystem's existing intelligence infrastructure. Maps raw sources for LLM Wiki ingestion planning. Leverages pre-built registries and indexes rather than re-scanning directories.
version: 1.0.0
category: coordination
type: reference
---

# Knowledge Source Reconnaissance

## When to Use

- Preparing raw source inventories for LLM Wiki implementation
- Planning knowledge base consolidation across workspace-hub
- Auditing what knowledge exists before building new pipelines
- Creating GitHub issues for knowledge infrastructure work
- Any task requiring a "what do we know and where is it" answer

## Core Principle

DO NOT re-scan directories. The workspace-hub ecosystem already has comprehensive intelligence infrastructure — read the registries, catalogs, and reports that already exist. Re-scanning is wasteful and misses the registry metadata (classification, status, relationships).

## The Three Intelligence Systems

The workspace ecosystem tracks knowledge across three layers:

1. **Document/Resource Intelligence** — Indexed local files (standards, conference papers, research literature, engineering refs)
2. **Online Intelligence** — Remote resources cataloged for future download (papers, tools, APIs, data portals)
3. **Repo Intelligence** — Engineering code, functions, standards implementations in digitalmodel repo

## Scan Procedure

Read these specific files — they are the authoritative sources:

### Phase 1: Document/Resource Intelligence

| File | What It Contains | Command |
|---|---|---|
| `data/document-index/index.jsonl` | Master document index (647K+ lines) | `wc -l` for line count |
| `data/document-index/enhancement-plan.yaml` | Classified files by domain (1M+ files) | Parse YAML, read `by_domain` section |
| `data/document-index/standards-transfer-ledger.yaml` | Standards tracking (status, impl, domains) | Read `summary` section |
| `data/document-index/conference-index.jsonl` | Conference paper catalog (27K+ papers) | `wc -l` for count |
| `data/document-index/conference-index-stats.yaml` | Conference stats per collection | `cat` for full stats |
| `data/document-index/research-literature-report.md` | Domain-organized research PDFs | `cat` for full breakdown |
| `data/document-index/engineering-refs-catalog.md` | Engineering reference files | `cat` for catalog |

### Phase 2: Online Intelligence

| File | What It Contains | Command |
|---|---|---|
| `data/document-index/online-resource-registry.yaml` | 247 remote resources (tools, repos, papers, APIs) | Read `summary` section for breakdown |
| `data/document-index/public-og-data-sources.yaml` | 38 data API/portal sources (ingested + pending) | Read `already_ingested`, `known_not_ingested`, `newly_discovered` |
| `data/document-index/conference-paper-catalog.yaml` | Conference paper metadata catalog | `wc -l` for scope |
| `data/document-index/intelligence-accessibility-registry.yaml` | Discoverability/accessibility map for intelligence assets; flags hard-to-discover registries/wikis | Read `assets` entries with `discoverability`/`gaps` |
| `data/document-index/resource-intelligence-maturity.yaml` | Canonical progress/coverage ledger for resource-intelligence parsing and review | Read `status` section |
| `data/document-index/resource-intelligence-maturity.md` | Human summary only; may be stale relative to YAML | Cross-check against YAML, do not treat as authoritative |

### Phase 3: Repo Intelligence

| Path | What It Contains | Command |
|---|---|---|
| `knowledge/seeds/*.yaml` | Structured knowledge (career learnings, law cases, mooring failures, naval arch resources) | `ls -la` + count entries per file |
| `knowledge-base/wrk-completions.jsonl` | Session work summaries (420 records) | `wc -l` |
| `knowledge/dark-intelligence/` | Excel-to-YAML extraction outputs | `find -name "*.yaml" | wc -l` |
| `digitalmodel/specs/module-registry.yaml` | Engineering function registry | `wc -l` for scope |
| `digitalmodel/` repo stats | 7,355 public functions, 42 standards impl | Read README.md or capability report |

### Phase 4: Mounted Filesystem Sources

| File | What It Contains |
|---|---|
| `data/document-index/mounted-source-registry.yaml` | 11 source roots with mount paths, dedup rules, availability checks |

Read the `source_roots` list — each entry has `source_id`, `mount_root`, `local_or_remote`, and `canonical_storage_policy`.

## Output Format

Produce a markdown table organized by intelligence system with columns: Source Name, Location, Scale/Count, Status, Notes. Always include a summary table with totals.

```
## SCALE SUMMARY

| Category | Count | Notes |
|---|---|---|
| Classified documents | 1,033,933 | 12 domains via enhancement-plan.yaml |
| Conference papers | 27,735 | 30 collections |
| Research literature | 174 | 12 domain folders |
| Online resources | 247 | 221 pending download |
| Data API sources | 38 | 20 ingestable |
| Knowledge seeds | ~100 | YAML entries across 5 files |
| Mounted filesystems | 11 | Local + remote mounts |
| Engineering functions | 7,355 | digitalmodel repo |
| Standards tracked | 425 | 424 indexed, 1 implemented |
```

## Key Insights

1. **The largest remaining semantic gap is summary coverage, not raw indexing** — `data-audit-report.md` shows 1,033,933 indexed records but only 639,585 with summaries (61.9%), leaving 394,348 records needing context enrichment.
2. **Index-level `other` still hides 44,705 project/miscellaneous files** — even though standards-level `other` has been eliminated, the document index still has a large miscellaneous bucket worth targeted reclassification.
3. **221 of 247 online resources have `download_status: not_started`** — massive untapped source pool.
4. **Intelligence discoverability is itself a gap** — `intelligence-accessibility-registry.yaml` flags assets like `online-resource-registry.yaml` as hard-to-discover / not linked from navigation surfaces.
5. **Knowledge seeds are NOT all indexed** by query-knowledge.sh — maritime-law-cases, mooring-failures, naval-architecture-resources are excluded.
6. **The riser-eng-job mount has 15,449 PDF/DOC/DOCX files** across 4 projects (93GB) — a major literature source.
7. **DDE remote mounts have 18 unique standard orgs** not present in /mnt/ace (ASME, AWS, NACE, etc.).
8. **Session corpus (wrk-completions.jsonl, 420 records)** represents tacit institutional knowledge — perfect for wiki ingest once structured.
9. **`resource-intelligence-maturity.md` can be stale; YAML is authoritative** — on 2026-04-13 the Markdown still said 5 docs / 0 read while YAML showed 425 docs / 29 read / 6.8%.
10. **`enhancement-plan.yaml` may lag current audits** — it still reported `by_domain.other.count: 176,527`, while newer audit artifacts reported index-level `other` at 44,705 and standards `other` eliminated.

## Pitfalls

- Do NOT attempt to `find` across /mnt/ace recursively — there are millions of files and it will hang
- Do NOT parse index.jsonl directly (572MB) — read the summary YAML/MD files instead
- Remote mounts (`/mnt/remote/`) may be unavailable — check mount status before attempting to read
- Enhancement-plan.yaml may be stale relative to later audit artifacts; verify against `data-audit-report.md` before citing `other` counts
- `resource-intelligence-maturity.md` is a convenience summary only; always trust the YAML ledger if numbers disagree
- Enhancement-plan.yaml is large — parse selectively, don't dump it whole
- Knowledge/dark-intelligence YAML files are gitignored — they exist locally but may not be on all machines

## Related Skills

- `llm-wiki` — the target system this inventory feeds into
- `knowledge-pipeline` — existing knowledge workflow skeleton
- `document-inventory` — generic single-directory scanner (don't use for workspace-hub recon)