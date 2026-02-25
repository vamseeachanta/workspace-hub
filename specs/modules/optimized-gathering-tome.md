---
title: "WRK-391: Online Resources Research — Implementation Plan"
description: "Phased web research across 8 categories to discover and catalog online resources for workspace-hub"
version: "1.0.0"
module: online-resources
status: draft
work_item: WRK-391
route: C
computer: [ace-linux-1, ace-linux-2]
---

# WRK-391: Online Resources Research — Plan

## Context

WRK-383 maps *local* documents to modules. WRK-391 asks: **what exists online that we don't yet know about?** This is active discovery across 8 categories (standards portals, data APIs, open-source tools, academic repos, professional body papers, real-time feeds, ESG data, AI/MCP ecosystem). The ecosystem already knows ~12-15 sources (BSEE, SODIR, NOAA, EIA, etc.) — the goal is to find 65+ genuinely new resources.

**Deliverables:**
1. `specs/online-resources/catalog.yaml` — ≥80 entries, machine-readable
2. `specs/online-resources/README.md` — narrative with "new discoveries" highlights
3. `specs/online-resources/follow-on-candidates.md` — ≥5 prioritized follow-on WRK items

## Catalog Schema

```yaml
entries:
  - name: "Resource Name"
    category: "open_data_apis"           # 8 category keys (snake_case)
    subcategory: "metocean"
    url: "https://..."
    auth_required: false
    cost_model: "free"                   # free | freemium | paid | academic | mixed
    relevance_score: 4                   # 1-5
    related_module: ["worldenergydata/metocean"]
    maturity: "live"                     # live | beta | sunset | unknown
    notes: "..."
    discovery_status: "new"              # known | new | investigate
    api_type: "REST"                     # optional: REST | GraphQL | bulk_download | scrape
    data_format: "JSON"                  # optional
    update_frequency: "daily"            # optional
    organization: "NOAA"                 # optional
```

## Execution Phases

### Phase 0: Setup (Orchestrator, ~10 min)

- Create `specs/online-resources/` directory
- Create skeleton `catalog.yaml`, `README.md`, `follow-on-candidates.md`
- Seed ~12-15 "known" entries from existing ecosystem (BSEE, SODIR, NOAA NDBC, CO-OPS, Open-Meteo, EIA, ERDDAP, MET Norway, BOEM, ANP, AER, CNH)
- Move WRK-391 to working

### Phase 1: Data-Centric Categories (2 parallel subagents, ~40 min)

| Subagent | Categories | Target | Key Searches |
|----------|-----------|--------|--------------|
| A | 2: Open Data APIs | ≥10 | Copernicus CDS/CMEMS, GEBCO, World Bank, IEA, IRENA, USGS, WRI, EIA v2 deep audit |
| B | 6+7: Real-Time Feeds + ESG | ≥5+5 | AIS tracking, NOAA GFS, USGS seismic, PSMSL tides, Climate TRACE, EDGAR, Carbon Monitor, CMIP6 |

**Gate G1**: 30+ total entries, Cat 2 ≥ 10, Cat 6 ≥ 5, Cat 7 ≥ 5

### Phase 2: Engineering Categories (2 parallel subagents, ~35 min)

| Subagent | Categories | Target | Key Searches |
|----------|-----------|--------|--------------|
| C | 1: Standards Portals | ≥5 | DNV free viewer, API MyCommittee, ISO previews, IMO GISIS, NSTA, IACS, ASME companion |
| D | 3: Open-Source Tools | ≥10 | MoorDyn, MAP++, OpenSees, CalculiX, Code_Aster, FEniCS, SU2, OpenGeoSys, wavespectra, openturns, SALib |

**Gate G2**: 45+ total entries, Cat 1 ≥ 5, Cat 3 ≥ 10

### Phase 3: Knowledge Categories (2 parallel subagents, ~45 min)

| Subagent | Categories | Target | Key Searches |
|----------|-----------|--------|--------------|
| E | 4: Academic Repos | ≥5 | arXiv cs.CE, OSTI.gov, Semantic Scholar API, Zenodo, DOAJ, OpenAIRE |
| F | 5: Professional Bodies | ≥10 | SPE OnePetro, SNAME, ASME JOMAE/OMAE, ISOPE, OTC, RINA, IMarEST, IOGP, TWI, AMPP |

Category 5 is the heaviest — each society entry needs notes on: free-access tier, embargo period, API/bulk access, self-archiving policies.

**Gate G3**: 60+ total entries, Cat 5 covers all 8 required societies (SPE, SNAME, ASME, ISOPE, OTC/OMAE, RINA, IOGP, TWI)

### Phase 4: AI/Agent Ecosystem (1 subagent, ~25 min)

| Subagent | Categories | Target | Key Searches |
|----------|-----------|--------|--------------|
| G | 8: AI/Agent/MCP | ≥10 | MCP registries (mcp.so, awesome-mcp-servers), prompt libraries, LangChain/CrewAI patterns, ISO 15926, PPDM, ML benchmarks, engineering LLM evals |

**Gate G4**: 70+ total entries, Cat 8 ≥ 10

### Phase 5: Synthesis & Finalization (Orchestrator, ~40 min)

1. Verify all category minimums met (gap-fill searches if needed)
2. URL verification pass on all entries
3. Write `README.md` narrative — top-5 per category + "new discoveries" highlight section
4. Generate `follow-on-candidates.md` — ≥5 prioritized WRK items
5. Cross-reference `related_module` against WRK-383 gap list
6. Run legal scan: `scripts/legal/legal-sanity-scan.sh`
7. Final commit, update WRK-391 frontmatter

## Subagent Architecture

```
ORCHESTRATOR (main)
  ├── Phase 1: Subagent-A (Cat 2) ‖ Subagent-B (Cat 6+7)
  ├── Phase 2: Subagent-C (Cat 1) ‖ Subagent-D (Cat 3)
  ├── Phase 3: Subagent-E (Cat 4) ‖ Subagent-F (Cat 5)
  ├── Phase 4: Subagent-G (Cat 8)
  └── Phase 5: Orchestrator synthesis
```

Each subagent: performs WebSearch → validates with WebFetch → returns YAML fragment → orchestrator merges into catalog.yaml.

## Quality Gates Summary

| Gate | After | Minimum Entries | Per-Category Checks |
|------|-------|-----------------|---------------------|
| G1 | Phase 1 | 30+ | Cat 2≥10, Cat 6≥5, Cat 7≥5 |
| G2 | Phase 2 | 45+ | Cat 1≥5, Cat 3≥10 |
| G3 | Phase 3 | 60+ | Cat 4≥5, Cat 5≥10, 8 societies covered |
| G4 | Phase 4 | 70+ | Cat 8≥10 |
| G5 | Phase 5 | 80+ | All minimums, README done, ≥5 follow-on WRKs, legal scan passes |

## Verification

- [ ] `catalog.yaml` exists with ≥80 entries across all 8 categories
- [ ] Per-category minimums met (5/10/10/5/10/5/5/10)
- [ ] Category 5 covers SPE, SNAME, ASME, ISOPE, OTC/OMAE, RINA, IOGP, TWI with free-access/embargo/API notes
- [ ] Every entry has `relevance_score`, `discovery_status`, `related_module`
- [ ] README.md "new discoveries" section with 10+ highlighted entries
- [ ] `follow-on-candidates.md` has ≥5 actionable WRK candidates
- [ ] At least 1 resource per gapped module from WRK-383
- [ ] Legal scan passes (exit code 0)

## Critical Files

| File | Purpose |
|------|---------|
| `.claude/work-queue/pending/WRK-391.md` | Requirements (8 categories, acceptance criteria) |
| `specs/data-sources/worldenergydata.yaml` | Existing YAML catalog schema to extend |
| `specs/templates/plan-template.md` | Plan template with cross-review gates |
| `.claude/work-queue/pending/WRK-383.md` | Module gap map for cross-referencing |
| `.claude/docs/orchestrator-pattern.md` | Subagent delegation pattern |
