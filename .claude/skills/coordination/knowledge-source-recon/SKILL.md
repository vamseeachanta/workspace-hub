---
name: knowledge-source-recon
description: Inventory authoritative knowledge registries and catalogs without rescanning the filesystem.
version: 1.0.0
author: Workspace Hub
category: coordination
tags: [knowledge, reconnaissance, inventory, catalogs, registries]
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
| `data/document-index/dde-standards-inventory.yaml` | DDE standards catalog (673 lines) | `wc -l` |
| `data/document-index/dde-literature-catalog.yaml` | DDE literature catalog (773 lines) | `wc -l` |
| `data/document-index/ship-plans-catalog.yaml` | Ship plans catalog (3,754 lines) | `wc -l` |

### Phase 2: Online Intelligence

| File | What It Contains | Command |
|---|---|---|
| `data/document-index/online-resource-registry.yaml` | 247 remote resources (tools, repos, papers, APIs) | Read `summary` section for breakdown |
| `data/document-index/public-og-data-sources.yaml` | 38 data API/portal sources (ingested + pending) | Read `already_ingested`, `known_not_ingested`, `newly_discovered` |
| `data/document-index/conference-paper-catalog.yaml` | Conference paper metadata catalog | `wc -l` for scope |

### Phase 3: Repo Intelligence

| Path | What It Contains | Command |
|---|---|---|
| `knowledge/seeds/*.yaml` | Structured knowledge (career learnings, law cases, mooring failures, naval arch resources) | `ls -la` + count entries per file |
| `knowledge-base/wrk-completions.jsonl` | Session work summaries (420 records) | `wc -l` |
| `knowledge/dark-intelligence/` | Excel-to-YAML extraction outputs | `find -name \*.yaml | wc -l` |
| `digitalmodel/specs/module-registry.yaml` | Engineering function registry | `wc -l` for scope |
| `digitalmodel/` repo stats | 7,355 public functions, 42 standards impl | Read README.md or capability report |

### Phase 4: Mounted Filesystem Sources

Read `data/document-index/mounted-source-registry.yaml` — each entry has `source_id`, `mount_root`, `local_or_remote`, and `canonical_storage_policy`.

## Output Format

Produce a markdown table organized by intelligence system with columns: Source Name, Location, Scale/Count, Status, Notes. Always include a summary table with totals.

## Key Insights

1. **The `other` domain has 176,527 unclassified files** — biggest raw source opportunity
2. **221 of 247 online resources have not_started download status** — massive untapped pool
3. **Conference papers total 22GB+ across 30 collections** — OMAE (10K), OTC (5.7K), ISOPE (4.2K)
4. **Knowledge seeds are NOT all indexed** — maritime-law-cases, mooring-failures, naval-architecture-resources excluded by query-knowledge.sh
5. **Riser-eng-job mount: 15,449 files across 4 projects (93GB)** — major literature source
6. **DDE remote mounts: 18 unique orgs** not in /mnt/ace (ASME, AWS, NACE, etc.)
7. **Session corpus: 420 WRK completions** — tacit institutional knowledge
8. **Resource-intelligence-maturity: 5 docs at 0%** — disconnected from WRK records

## Pitfalls

- Do NOT attempt to `find` across /mnt/ace recursively — millions of files, will hang
- Do NOT parse index.jsonl directly (572MB) — read summary YAML files instead
- Remote mounts (`/mnt/remote/`) may be unavailable — check mount status first
- Enhancement-plan.yaml is 1.7MB — parse with yaml.safe_load, don't `cat`
- Dark-intelligence YAML files are gitignored — local only
