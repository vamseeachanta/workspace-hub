# LLM-Wiki External-Source Priority Queue

> **Issue:** [#2242](https://github.com/vamseeachanta/workspace-hub/issues/2242)
> **Parent umbrella:** [#2241](https://github.com/vamseeachanta/workspace-hub/issues/2241)
> **Architecture:** [#2205](https://github.com/vamseeachanta/workspace-hub/issues/2205) operating model
> **Date:** 2026-04-14
> **YAML artifact:** `data/document-index/llm-wiki-external-source-priority-queue.yaml`

---

## 1. Purpose

This document prioritizes external source families for LLM-wiki strengthening using existing registries and intelligence surfaces. The goal is to maximize wiki readiness improvement per token spent, focusing on thinner wiki domains first.

## 2. Wiki Domain Gap Analysis

| Wiki Domain | Pages | Gap Severity | Strengthening Priority |
|---|---:|---|---|
| engineering | 81 | High | Primary target for P1/P2 sources |
| naval-architecture | 45 | High | Primary target for P1/P2 sources |
| maritime-law | 22 | High | Secondary (fewer relevant sources) |
| marine-engineering | 19,172 | Low | Selective — only high-value additions |
| personal | 0 | Deferred | Out of scope for external-source work |

## 3. Source Family Prioritization

### P1 — High ROI, Promotable Now

| Family | Entries | Promotion Strategy | Target Wikis | Related Issues |
|---|---:|---|---|---|
| Online Data APIs & Standards Portals | 40 | metadata-first | engineering, marine-eng, naval-arch | #1609, #2039, #2067 |
| Indexed Conference Papers (DOT/OMAE/ISOPE) | ~18,000 PDFs | summary-backed | marine-eng, naval-arch, engineering | #2001, #2039, #2067, #2068 |
| Standards with Existing Summaries | ~639,000 | summary-backed | engineering, marine-eng | #2216, #2207, #2039 |

### P2 — Medium ROI, Bounded Extraction

| Family | Entries | Promotion Strategy | Target Wikis | Related Issues |
|---|---:|---|---|---|
| Online GitHub Repos & Tools | 153 | metadata-first | engineering, marine-eng | #2039, #2042 |
| Online Papers & Tutorials | 46 | summary-backed | engineering, marine-eng, naval-arch | #2039, #2067 |
| Research Literature (Mounted) | 7 domains | raw-extraction-needed | engineering, marine-eng, naval-arch | #2034, #2039 |

### P3 — Low ROI or High Token Cost

| Family | Entries | Promotion Strategy | Target Wikis | Related Issues |
|---|---:|---|---|---|
| Unindexed Conference Papers | ~4,000 PDFs | raw-extraction-needed | marine-eng, engineering | #2001 |
| DDE Literature (Remote) | 5,456 PDFs | raw-extraction-needed | engineering, marine-eng | #2034 |

## 4. Promotion Strategy Definitions

| Strategy | Token Cost | When to Use | Evidence Required |
|---|---|---|---|
| **metadata-first** | Low | Structured API/tool metadata already exists in registry notes | Registry notes field with capability summary |
| **summary-backed** | Medium | L2 index summaries or phase_a abstracts exist | Existing JSONL index entries or summary fields |
| **raw-extraction-needed** | High | No existing summaries; requires PDF parsing | Mount access + extraction pipeline |
| **registry-only** | None | Keep in registry but do not promote to wiki | N/A — explicit deferral |

## 5. Source Family Details

### 5.1 Online Data APIs & Standards Portals (P1)

**Source:** `data/document-index/online-resource-registry.yaml` (type: data_api, standard_portal)

Key entries include:
- ERA5/Copernicus (hindcast data for metocean)
- NOAA NDBC (buoy observation data)
- DNV Standards Explorer (650+ rules)
- API Addenda/Errata Portal (standards currency)
- BOEM/BSEE (offshore lease and production data)
- EIA Open Data API (energy data)
- SODIR FactPages (Norwegian shelf data)
- Open-Meteo Marine API (real-time wave forecasts)

**Why P1:** Registry notes already contain structured capability descriptions. Promoting to wiki stubs is a reformatting task — no source reading required. Directly fills engineering and naval-architecture wiki gaps.

### 5.2 Indexed Conference Papers (P1)

**Source:** `data/document-index/conference-paper-catalog.yaml` (indexed collections)

| Collection | Files | PDFs | Domain Focus | Indexing |
|---|---:|---:|---|---|
| DOT | 7,516 | 1,456 | subsea, pipeline | phase_a_complete |
| OMAE | 10,130 | 7,292 | structural, marine | phase_a_complete |
| ISOPE | 4,183 | 4,074 | marine, hydrodynamics | phase_a_complete |

**Why P1:** Phase_a indexing (from #2001 batch ingest work) provides title/abstract/domain data. Cross-reference with `conference-index-batch.jsonl` and `conference-phase-a-results.jsonl` for existing outputs.

### 5.3 Standards with Existing Summaries (P1)

**Source:** `data/document-index/resource-intelligence-maturity.yaml`

- 1,033,933 total index records
- 639,585 existing summaries (61.9% coverage)
- 425 standards in active maturity scope
- 10 standards domains after reclassification

**Why P1:** Over 600k summaries already exist in the document index. Domain-by-domain promotion to wiki pages requires only reformatting and cross-linking, not re-reading source PDFs.

### 5.4 Online GitHub Repos & Tools (P2)

**Source:** `data/document-index/online-resource-registry.yaml` (type: github_repo, tool)

153 entries covering CAD tools (CadQuery, Gmsh, NGSolve, PythonOCC), wave/ocean tools (wavespectra), CFD tools, data-science tools, and MCP server registries.

**Why P2:** Useful for engineering wiki tool-profile pages. Many already have structured notes. Network access needed for README scraping of entries without sufficient existing metadata.

### 5.5 Research Literature — Mounted (P2)

**Source:** `data/document-index/mounted-source-registry.yaml` (source_id: research_literature_local)

Seven domain directories at `/mnt/ace-data/digitalmodel/docs/domains`:
cathodic_protection, geotechnical, hydrodynamics, naval_architecture, pipeline, structural, subsea.

**Why P2:** High domain relevance but requires PDF extraction pipeline. Should be sequenced after metadata-first families complete. Each domain has a `download-literature.sh` script with provenance URLs.

## 6. Do-Not-Process-Yet List

| Source | Reason | Revisit Trigger |
|---|---|---|
| Riser engineering archives (15,449 files, 93 GB) | Too large and specialized; needs dedicated scoping issue | Dedicated riser-wiki issue created |
| The Well dataset (15 TB simulations) | Unsuitable for wiki pages; useful only for computation modules | Never for wiki |
| General/non-domain tools (MCP servers, etc.) | Low ROI for engineering wiki domains | Engineering wiki adds tooling section |
| Course materials (3 entries) | Too few entries for batch processing | Registry grows beyond 10 entries |
| Professional body publications (4 entries) | Behind access restrictions; manual download required | #1609 adds auth-gated source support |

## 7. Recommended Execution Order

| Step | Source Family | Batch Pack | Overnight Safe |
|---:|---|---|---|
| 1 | Online Data APIs & Standards Portals | batch-pack-1 | Yes |
| 2 | Indexed Conference Papers (DOT/OMAE/ISOPE) | batch-pack-2 | Yes |
| 3 | Standards with Existing Summaries | batch-pack-4 | Yes |
| 4 | Online GitHub Repos & Tools | batch-pack-3 | Conditional |
| 5 | Online Papers & Tutorials | — | Yes |
| 6 | Research Literature (Mounted) | — | Yes |
| 7 | Unindexed Conference Papers + DDE Literature | — | No |

## 8. Token-Efficiency Rules

These rules apply to all queue execution:

1. **Prefer metadata-first promotion** when registry notes contain sufficient evidence
2. **Never re-read source PDFs** when L2/L3 summaries already exist
3. **Batch by source family and target wiki domain** to minimize context-switching
4. **Keep execution slices small enough** for single unattended agent runs
5. **Create follow-on issues** rather than silently expanding scope when new sources are discovered
6. **Check existing wiki pages** before creating stubs to avoid duplicates
7. **Reference provenance** — every promoted wiki stub must trace back to its source registry entry

## 9. Issue Dependency Map

```
#2241 (umbrella)
├── #2242 (this queue) ← YOU ARE HERE
├── #2243 (batch packs) ← companion deliverable
├── #2244 (ACMA breadth triage)
│
├── Pre-existing execution issues to reuse:
│   ├── #1609 (download automation pipeline)
│   ├── #2001 (conference batch-ingest — closed, precedent)
│   ├── #2034 (wiki ingestion pipeline)
│   ├── #2039 (engineering wiki ingest — remaining high-value sources)
│   ├── #2040 (cronize engineering wiki ingest)
│   ├── #2042 (skill metadata as wiki pages)
│   ├── #2067 (wire .planning/research into wiki ingest)
│   ├── #2068 (cross-link JSONL package)
│   └── #2121 (weekly query packs / verification fixtures)
│
├── Architecture foundations (read-only):
│   ├── #2205 (operating model)
│   ├── #2207 (provenance/reuse contract)
│   ├── #2208 (retrieval contract)
│   └── #2209 (durable/transient boundary)
│
└── Linked spine: #2248 (prioritization ordering)
```
