# Wiki Log: engineering

> Chronological record of all wiki operations.
> Format: ## [YYYY-MM-DD] operation | Title

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
