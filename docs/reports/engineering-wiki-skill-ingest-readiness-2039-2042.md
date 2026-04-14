# Engineering Wiki — Skill Ingest Readiness Report

> Planning artifact for #2039 and #2042
> Generated: 2026-04-14 by Claude (fallback for failed Gemini batch)
> Branch: `issue-2039-2042-gemini-research`

## 1. Current Wiki Baseline

The engineering wiki has **75 pages** across 5 categories, sourced from 12 ingested source classes:

| Category | Pages |
|----------|-------|
| Concepts | 31 |
| Entities | 22 |
| Sources | 12 |
| Standards | 7 |
| Workflows | 3 |
| **Total** | **75** |

Reference: `knowledge/wikis/engineering/wiki/index.md`

## 2. Skill Inventory — Quantification

### Active Skills

- **796 active skills** across 35 top-level families (excludes 2,100 archived)
- **87 engineering skills** in `.claude/skills/engineering/` across 12 subcategories
- **9 pages** already ingested from skills metadata (Source Class 9 per `SOURCE_INVENTORY.md`)

### Engineering Skill Families

| Family | Path | Skills | Wiki Pages | Gap |
|--------|------|--------|------------|-----|
| marine-offshore/orcaflex | `.claude/skills/engineering/marine-offshore/orcaflex/` | 25 | 1 entity | 24 sub-skills uningested |
| marine-offshore (individual) | `.claude/skills/engineering/marine-offshore/` | 22 | 7 pages (partial) | ~14 skills uningested |
| marine-offshore/orcawave | `.claude/skills/engineering/marine-offshore/orcawave/` | 8 | 1 entity | 7 sub-skills uningested |
| standards | `.claude/skills/engineering/standards/` | 5 | 7 (from other sources) | 5 family-level skills uningested |
| cad | `.claude/skills/engineering/cad/` | 5 | 0 | 5 (entirely new domain) |
| marine-offshore/aqwa | `.claude/skills/engineering/marine-offshore/aqwa/` | 5 | 1 entity | 4 sub-skills uningested |
| gis | `.claude/skills/engineering/gis/` | 4 | 0 | 4 (entirely new domain) |
| doc-extraction | `.claude/skills/engineering/doc-extraction/` | 4 | 0 | 4 workflow pages |
| drilling | `.claude/skills/engineering/drilling/` | 2 | 0 | 2 (new domain) |
| cfd | `.claude/skills/engineering/cfd/` | 1 | 1 entity | 0 (covered) |
| other (units, oil-gas, maritime-legal, financial, FFS) | various | 6 | ~2 partial | ~4 uningested |
| **Totals** | | **87** | **~9 dedicated** | **~73 uningested** |

### Non-Engineering but Potentially Relevant

| Family | Path | Skills | Engineering Relevance |
|--------|------|--------|----------------------|
| digitalmodel | `.claude/skills/digitalmodel/` | 3 | 1 relevant (`naval-architect-expert`) |
| science | `.claude/skills/science/` | 6 | 0 (bio-research only) |
| mlops | `.claude/skills/mlops/` | 22 | 0 (ML infrastructure, not engineering domain) |
| data-science | `.claude/skills/data-science/` | 1 | 0 (Jupyter tooling) |

### Other Uningested Source Classes (#2039 scope)

| Source | Total | Ingested | Remaining | Reference |
|--------|-------|----------|-----------|-----------|
| Closed `cat:engineering` issues | 79 | 5 | 74 | GitHub label search |
| Closed `cat:engineering-calculations` issues | 13 | 0 | 13 | GitHub label search |
| Mooring failure seed entries | 40 | 7 | 33 | `knowledge/seeds/mooring-failures-lng-terminals.yaml` |
| Nightly research outputs | 12+ | 1 | ~11 | `.planning/research/` |

## 3. Overlap vs. Gaps Analysis

### Well-Covered (wiki pages exist from skills or other sources)

These skill areas already have dedicated wiki pages. New skill ingest would add depth, not breadth:

- **OrcaFlex** — entity page `entities/orcaflex-solver.md` covers root; 25 sub-skills add analysis-type depth
- **OrcaWave** — entity page `entities/orcawave-solver.md`; 8 sub-skills add QTF/mesh/damping depth
- **AQWA** — entity page `entities/aqwa-solver.md`; 5 sub-skills add input/output/benchmark depth
- **OpenFOAM** — entity `entities/openfoam-cfd.md` + concept `concepts/cfd-offshore-hydrodynamics.md`
- **Mooring** — entity + concept pages; mooring-design skill extends existing coverage
- **Hydrodynamics** — concept page exists; hydrodynamic-analysis skill is redundant
- **Fatigue** — 2 concept pages (fatigue-analysis-offshore, sn-curve-fatigue-definitions); skill coverage aligns
- **Standards** — 7 standard pages from seeds/issues; 5 standard-family skills offer overview-level additions

### Gaps (no wiki coverage from any source)

These skill areas have **zero** wiki pages and represent entirely new domain coverage:

| Gap Domain | Skills | Expected Pages | Value Assessment |
|------------|--------|----------------|------------------|
| **CAD/Meshing** | FreeCAD, GMSH, PyVista, Blender, CAD Engineering | 5-7 | High — design visualization toolchain |
| **GIS/Spatial** | QGIS, Google Earth Engine, Python GIS, GIS Workflow | 4-6 | Medium — spatial analysis for offshore siting |
| **Doc Extraction** | 4 domain-specific extraction skills | 3-4 | Medium — reusable workflow methodology |
| **Drilling** | Drillbotics, Drilling Engineering | 2-3 | Medium — new engineering domain |
| **OrcaFlex Analysis Types** | installation, jumper, extreme, modal, operability, etc. | 8-12 | Highest — deep domain analysis knowledge |
| **OrcaWave Analysis Types** | QTF, damping sweep, multi-body, mesh gen | 4-6 | High — extends core hydrodynamic tooling |
| **Risk Assessment** | risk-assessment skill | 1-2 | Medium — cross-cutting methodology |
| **Signal Analysis** | signal-analysis skill | 1 | Low — niche utility |
| **Production Engineering** | production-engineering skill | 1-2 | Medium — new subsurface domain |
| **Asset Integrity** | fitness-for-service skill | 1 | Low — API 579 page partially covers |
| **Maritime Legal** | maritime-legal skill | 1 | Low — adjacent, not core engineering |
| **Units** | units skill | 1 | Low — utility, not domain knowledge |

### Summary

- **73 of 87** engineering skills have no dedicated wiki page
- **2 entirely new domains** (CAD, GIS) would be opened by skill ingest
- **Estimated yield**: 40-60 new wiki pages from skills alone
- Combined with other #2039 sources (issues, mooring failures, research): **55-80 new pages** total potential

## 4. Top 3 Recommended Execution Slices

### Slice 1: OrcaFlex Sub-Skill Expansion (Highest Priority)

**Why first**: The 25 OrcaFlex sub-skills contain the deepest domain knowledge in the repo — specific analysis types (installation, jumper, extreme, modal, operability, visualization) that directly serve engineering delivery. This is the highest-value-per-token slice.

- **Source**: `.claude/skills/engineering/marine-offshore/orcaflex/` (25 skills)
- **Expected yield**: 8-12 pages (group related sub-skills into thematic pages)
- **Page types**: concepts (analysis methods) + workflows (specific analysis pipelines)
- **Overlap risk**: Low — root entity exists, but sub-skill depth is entirely new
- **Grouping strategy**: batch, extreme, installation, jumper, modal, operability, post-processing, visualization, model-management (sanitization, generator, monolithic-to-modular)

### Slice 2: CAD + GIS Domain Bootstrap (Zero-Overlap)

**Why second**: Opens two entirely new wiki domains with zero overlap risk. These skills represent operational toolchain knowledge that compounds with existing solver pages.

- **Source**: `.claude/skills/engineering/cad/` (5) + `.claude/skills/engineering/gis/` (4)
- **Expected yield**: 6-8 pages
- **Page types**: entities (tools) + concepts (methodologies)
- **Overlap risk**: None
- **Notable**: FreeCAD + GMSH pair naturally; PyVista links to existing OrcaFlex/OpenFOAM visualization needs

### Slice 3: Standards Family + Closed Issues Deep Dive

**Why third**: Extends the wiki's most-referenced material (standards) and unlocks 87 uninvestigated closed issues as a knowledge source.

- **Source**: `.claude/skills/engineering/standards/` (5 family skills) + 74 closed `cat:engineering` issues + 13 `cat:engineering-calculations` issues
- **Expected yield**: 8-12 pages (3-5 from standards families, 5-7 from instructive issues)
- **Page types**: standards (family overviews) + concepts (from issue decisions)
- **Overlap risk**: Medium for standards (existing pages from other sources); Low for issues
- **Triage needed**: Issues require a scan pass to identify the ~10 most instructive ones

## 5. Execution Readiness Assessment

| Criterion | Status | Notes |
|-----------|--------|-------|
| Source material accessible | READY | All skills are git-tracked, readable |
| Wiki schema documented | READY | `SCHEMA.md` defines page format |
| Ingest conventions documented | READY | `SOURCE_INVENTORY.md` has rules |
| Template/format examples | READY | 75 existing pages as exemplars |
| Duplicate detection needed | YES | Must check index before creating pages |
| Cross-reference targets exist | YES | Existing 75 pages provide link targets |
| Lint infrastructure | READY | Wiki lint checks orphans, broken refs |
| Estimated total new pages | 40-60 | From skills alone; 55-80 with all #2039 sources |
| Issues needing plan approval | #2039, #2042 | Neither has `status:plan-approved` yet |

## 6. Risk Factors

1. **Thin skills**: Some sub-skills may contain minimal domain knowledge (just tool flags). Triage during ingest to skip pure-CLI-reference skills.
2. **Grouping judgment**: The 25 OrcaFlex sub-skills need thoughtful grouping — too many fine-grained pages dilute the wiki; too few lose specificity.
3. **Standards overlap**: 7 standard pages already exist from other sources. New standards-family skills should create overview pages that link to existing specific-standard pages, not duplicate them.
4. **Issue triage cost**: Scanning 87 closed issues for instructive content requires a dedicated pass before ingest.

## References

- Issue #2039: [engineering wiki — ingest remaining high-value sources](https://github.com/vamseeachanta/workspace-hub/issues/2039)
- Issue #2042: [engineering wiki — ingest skill metadata as wiki pages](https://github.com/vamseeachanta/workspace-hub/issues/2042)
- Wiki index: `knowledge/wikis/engineering/wiki/index.md` (75 pages)
- Source inventory: `knowledge/wikis/engineering/SOURCE_INVENTORY.md` (12 classes)
- Skills root: `.claude/skills/engineering/` (87 active skills across 12 subcategories)
