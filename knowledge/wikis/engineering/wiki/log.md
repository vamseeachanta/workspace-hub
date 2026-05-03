# Wiki Log: engineering

> Chronological record of all wiki operations.
> Format: ## [YYYY-MM-DD] operation | Title

## [2026-05-02] ingest | OCIMF-TANDEM-MOORING promotion (#2227)
- Pages created: `standards/ocimf-tandem-mooring.md` — first-edition 2009 OCIMF Tandem Mooring & Offloading Guidelines for Conventional Tankers at F(P)SO Facilities; grounded in `data/document-index/summaries/sha256:5e5f...json` (#2521 OCR preview, first 3 pages).
- Pages updated: `standards/ocimf-meg4.md` (added one row to `## Related Standards` table linking to tandem page); `index.md` (Standards section bumped 7→8 pages, page_count 82→83, last_updated 2026-05-02, tandem row added); `concepts/mooring-line-failure-physics.md` (inbound `[OCIMF-TANDEM-MOORING]` related-standard link added).
- Gate-input update: `docs/reports/acma-wiki-unblock-2245-handoff.yaml` top-level `ready_for_2227` flipped false→true with inline comment documenting rollup-semantics shift (CSA scope formally split to #2522 on 2026-04-23; per-target rows unchanged).
- Source: `data/document-index/summaries/sha256:5e5f61e785295f0ac849399bb302cb5192ca84c108e6a57e82b8cc83b8b431af.json` (528-char `summary`, ~1.5KB `text_preview`).
- Issue: #2559 executes the v5 Branch A contract from #2227 (CLOSED 2026-05-02 by user override); plan at `docs/plans/2026-05-02-issue-2559-ocimf-tandem-wiki-source-promotion.md` SHA `5a8655272`.
- Out of scope: CSA Z276.1-20 + Z276.18 promotion (→ #2522); raw OCIMF PDF ingestion; full-text OCR.

## [2026-04-28] deep-extraction | Elements QGIS flowline/DEM corpus (#2536)
- Pages created: `sources/elements-qgis-flowline-dem-deep-extraction.md`, `workflows/qgis-flowline-dem-preprocessing.md`.
- Extraction artifacts: `.planning/intel/elements-deep-extraction/gis/dem-stats.json`, `gis/dxf-entity-summary.json`, `gis/qgis-files.json`.
- Notes: Raw GIS/CAD files remain link-only in `/mnt/ace/digitalmodel/tools/qgis`; `.tif` suffix was found to contain ASCII-grid style DEM content.

## [2026-04-26] add | Canonical Spec Semantic Equivalence Contract + Fixture Expansion Cookbook (#2476)
- Pages created:
  - `concepts/canonical-spec-semantic-equivalence.md` — defines semantic equivalence dimensions for canonical `spec.yml` -> native OrcaWave/OrcaFlex YAML; nine dimensions plus reverse-parser equivalence and anti-pattern catalogue
  - `workflows/orcawave-orcaflex-fixture-expansion-cookbook.md` — procedure for adding new structure-family fixtures with formatting-robust assertions; references licensed-proof boundary
- Pages updated:
  - `workflows/orcawave-to-orcaflex-pipeline.md` — added Proof Boundary section distinguishing semantic equivalence (CI) from licensed load/run (paid machine); cross-linked to new contract and cookbook
  - `index.md` — added rows for new concept and workflow; bumped page_count 77 -> 79; bumped concept count 31 -> 32; bumped workflow count 3 -> 4
- Scope: docs-only; no `digitalmodel/` source or test files were touched
- Downstream consumers: #2472, #2473, #2474, #2475 (next-wave semantic-proof issues); #2455, #2456, #2457 are first-wave (CLOSED)
- Source intel: `docs/handoffs/2026-04-23-orcawave-orcaflex-semantic-proof-exit-handoff.md` listed six llm-wiki gaps; this issue closes gaps #1 (contract) and #6 (cookbook); gaps #2-#5 remain in scope of #2472-#2475
- Plan: `docs/plans/2026-04-23-issue-2476-llm-wiki-semantic-equivalence-contract.md`

## [2026-04-17] ingest | HN CadQuery Discussion (Python parametric CAD)
- Processed: https://news.ycombinator.com/item?id=47772725 (180 points, 47 comments, submitted by gregsadetsky)
- Pages created: sources/2026-04-17-hn-cadquery.md, entities/cadquery.md
- Pages updated: index.md (entity + source row, counts: 75→77 pages, 12→13 sources)
- Cross-wiki: created mirror entity at marine-engineering/wiki/entities/cadquery.md
- Notes: CadQuery = Python on OpenCASCADE B-rep kernel. Relevance: digitalmodel/, CAD-DEVELOPMENTS/, parametric offshore hardware families.
- Follow-up issues: #2327 (digitalmodel spike), #2328 (build123d/ReplicAD/FluidCAD compare), #2329 (code-first vs GUI CAD methodology).

## [2026-04-08] init | Wiki scaffolded
- Created by: `uv run scripts/knowledge/llm_wiki.py init engineering`
- Directories: raw/, wiki/entities, wiki/concepts, wiki/sources, wiki/comparisons, wiki/visualizations
- CLAUDE.md customized for repo engineering methodology scope

## [2026-04-08] seed-ingest | Initial seed from 5 source classes
- Source class 1: docs/methodology/ (6 files) -> 6 concept pages
- Source class 2: docs/modules/ (selective) -> 3 concept pages + 5 source pages
- Source class 3: .claude/memory/topics/ (selective) -> 3 concept pages
- Source class 4: docs/architecture/ (selective) -> 2 entity pages
- Source class 5: knowledge seeds (implicit via cross-references)
- Pages created: 12 concepts, 10 entities, 5 sources = 27 new pages
- Pre-existing pages found: 6 (from prior domain ingests)
- Total pages: 33
- Index, overview, and log updated
- SOURCE_INVENTORY.md created with ingest conventions
- Notes: Issue #2034 initial seed — methodology + module docs + architecture.

## [2026-04-09] incremental-ingest | 4 new source classes (#2039)
- Source class: skills-metadata (.claude/skills/engineering/) -> 4 entity pages + 5 concept pages
  - entities: mooring-analysis-system, diffraction-analysis-system, naval-architecture-skill, openfoam-cfd, orcawave-solver
  - concepts: wave-theory-offshore, seakeeping-6dof, structural-analysis-offshore, fatigue-analysis-offshore, hydrodynamic-analysis
- Source class: mooring-failures-seed (knowledge/seeds/mooring-failures-lng-terminals.yaml) -> 4 entity pages + 1 concept page
  - entities: nws-lng-mooring-investigation, hmpe-mooring-failures, prelude-flng-mooring, elba-island-mooring-incident
  - concept: mooring-line-failure-physics
- Source class: closed-issues (cat:engineering GitHub issues) -> 2 concept pages + 1 workflow page
  - concepts: free-span-viv-fatigue, field-development-economics
  - workflow: orcawave-to-orcaflex-pipeline
- Source class: research-outputs (.planning/research/) -> 1 concept page
  - concept: standards-update-tracking
- Standards pages created: 3 (dnv-os-e301, dnv-rp-f105, ocimf-meg4)
- Source summary pages created: 4 (skills-metadata, mooring-failures-seed, closed-engineering-issues, research-outputs)
- Pages created this pass: 23
- Total pages: 75 (31 concepts, 22 entities, 12 sources, 7 standards, 3 workflows)
- Index, log, SOURCE_INVENTORY updated
- Notes: Issue #2039 — ingested 4 remaining high-value source classes.

## [2026-04-08] seed-ingest-2 | Expanded seed from career-learnings, dark-intelligence, session-memory
- Source class: career-learnings (knowledge/seeds/career-learnings.yaml) -> 7 concept pages
  - pipeline-integrity-assessment, viv-riser-fatigue, fea-structural-analysis, cfd-offshore-hydrodynamics
  - cathodic-protection-design, energy-field-economics, ai-drill-well-on-paper
- Source class: dark-intelligence (knowledge/dark-intelligence/) -> 2 concept pages
  - pile-capacity-alpha-method, sn-curve-fatigue-definitions
- Source class: session-memory (.claude/memory/KNOWLEDGE.md, solver lessons) -> 3 entity + 2 workflow pages
  - entities: orcaflex-solver, aqwa-solver, bemrosetta-tool
  - workflows: solver-debugging-protocol, parametric-engineering-reports
- Source class: career-learnings/software -> 3 concept pages
  - shell-scripting-patterns, python-type-safety, jsonl-knowledge-stores
- Standards reference pages created: 4 (dnv-rp-f101, api-579-ffs, dnv-rp-c203, dnv-rp-c205)
- Source summary pages created: 3 (career-learnings-seed, dark-intelligence-extractions, methodology-docs)
- Pages created this pass: 24
- Total pages: 52 (25 concepts, 13 entities, 8 sources, 4 standards, 2 workflows)
- Index, overview updated with complete inventory
- Notes: Issue #2034 seed complete. 5+ source classes ingested, 52 pages total. Incremental ingest workflow documented in CLAUDE.md and SOURCE_INVENTORY.md.

## [2026-04-28 19:24 UTC] batch-ingest | Batch 1 (2 records)
- Domain: engineering
- Records: 2
- Titles (sample): Elements ingest catalog — digitalmodel-q, Elements ingest catalog — doris-universi
- Pages created: wiki/sources/<slug>.md for each record
- Index updated: wiki/index.md

## [2026-04-29] ingest | Doris University metadata-first tranche 1 (#2542)
- Pages created: 7 source pointers and 8 curated concept shells.
- Standards resolver: `engineering-standards/wiki/standards/api-17e.md` public-metadata-only stub.
- Source of record: `/mnt/ace/doris/training`; no raw training decks, figures, full text, OCR output, or standards excerpts copied.
