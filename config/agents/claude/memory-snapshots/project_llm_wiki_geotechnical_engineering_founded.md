---
name: llm-wiki-geotechnical-engineering-domain-founded
description: 13th llm-wiki domain founded 2026-05-18 via the LinkedIn-ingest workflow; founding source Xu (2026) SoilModelsPy Python package for soil constitutive modeling
metadata: 
  node_type: memory
  type: project
  originSessionId: 578c6ffe-2428-405f-9435-a7eebec611a4
---

The `wikis/geotechnical-engineering/` domain at `vamseeachanta/llm-wiki` was founded on 2026-05-18 (commit `bbc21cb7` pre-rebase, `c6f76539` post-rebase). It is the 13th domain wiki in the llm-wiki ecosystem (sibling set as of this date: acma-projects, asset-management, drilling-engineering, engineering, engineering-standards, geotechnical-engineering, lng-projects, marine-engineering, maritime-law, naval-architecture, production-engineering, reservoir-engineering, trends-and-strategies).

**Why:** Soil mechanics and soil constitutive modeling (PM4Sand, PM4Silt, NorSand, Modified Cam-Clay, MIT-S1, Hujeux, UBCSAND, hypoplasticity) are a distinct sub-discipline of continuum mechanics that does not fit cleanly under `engineering/` (which has offshore soil-structure-interaction pages — `pile-capacity-alpha-method`, `pipeline-soil-interaction`, `riser-soil-interaction` — that are the offshore-application surface, not the constitutive-modeling-and-soil-physics surface). Forcing geotech into `engineering/` would have created sunk-cost migration debt later. Founding decision was authorized via AskUserQuestion at routing time.

**How to apply:**
- When a future LinkedIn or paper ingest touches soil constitutive models, lab tests (triaxial, DSS, oedometer, resonant column), site characterization (CPT, SPT, vane shear, geophysics), foundations (shallow + deep), earthquake geotechnical engineering, slope stability, retaining structures, ground improvement, or open-source soil-mechanics tooling — route to `wikis/geotechnical-engineering/`.
- Do **not** duplicate the existing `engineering/wiki/concepts/{pile-capacity-alpha-method,pipeline-soil-interaction,riser-soil-interaction}.md` pages here; cross-link to them.
- Founding source: `wikis/geotechnical-engineering/wiki/sources/xu-2026-soilmodelspy.md`. Founding seed roadmap in `wikis/geotechnical-engineering/wiki/overview.md` lists ~12 anticipated near-term ingests (Boulanger-Ziotopoulou UC Davis CGM PM4Sand/PM4Silt reports, Wood 1990 Cambridge textbook, ASTM D2435/D4767/D6528, API RP 2GEO, ISO 19901-4, Eurocode 7, and constitutive-model concept pages).

**Related:** [[project_llm_wiki_trends_and_strategies_founded]] (sibling founding, same session); [[project_llm_wiki_external_post_ingest_workflow]] (workflow used to execute the founding).
