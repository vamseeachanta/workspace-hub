# Engineering Wiki — Source Inventory

> Defines which repo sources feed the engineering wiki and how to ingest them.

## Source Classes

### Class 1: Methodology Docs (`docs/methodology/`)
**Priority**: Highest — these are the repo's core engineering philosophy.
**Files**: 6 markdown documents
**Page type**: Concepts (one concept page per methodology doc)
**Ingest rule**: Read full doc, extract core insight, create concept page with tags and cross-refs.

| Source File | Wiki Page |
|-------------|-----------|
| compound-engineering.md | concepts/compound-engineering.md |
| enforcement-over-instruction.md | concepts/enforcement-over-instruction.md |
| orchestrator-worker.md | concepts/orchestrator-worker-separation.md |
| multi-agent-parity.md | concepts/multi-agent-parity.md |
| compliance-dashboard.md | concepts/compliance-dashboard.md |
| knowledge-to-website-pipeline.md | concepts/knowledge-to-website-pipeline.md |

### Class 2: Module Documentation (`docs/modules/`)
**Priority**: High — captures operational patterns across 16 domains.
**Files**: 136 markdown documents across 16 subdirectories
**Page type**: Entities (tools/systems) + Concepts (patterns)
**Ingest rule**: Read doc, classify as entity or concept, create page. Group related docs into single pages where they cover the same topic.

Key subdirectories (initial seed):
- `ai/` (35 files) — agent workflows, delegation, equivalence
- `architecture/` (6 files) — system design patterns
- `automation/` (11 files) — orchestration, centralization
- `testing/` (17 files) — TDD, pytest, deployment strategy
- `standards/` (7 files) — compliance, file organization, HTML reports
- `workflow/` (6 files) — development workflow, guidelines
- `ci-cd/` (7 files) — CI/CD integration, GitHub Actions

### Class 3: Session Learnings (`.claude/memory/topics/`)
**Priority**: Medium — distilled operational wisdom from real sessions.
**Files**: 19 markdown files (feedback rules, patterns, machine config)
**Page type**: Concepts (operational patterns) + Sources (session summaries)
**Ingest rule**: Group related feedback topics into thematic concept pages. Individual machine/config topics become entity pages.

### Class 4: Architecture Docs (`docs/architecture/`)
**Priority**: High — system architecture and component maps.
**Files**: 4 markdown documents
**Page type**: Entities (specific systems)
**Ingest rule**: One entity page per architecture doc.

### Class 5: Knowledge Seeds (`knowledge/seeds/`)
**Priority**: Medium — existing curated knowledge in YAML format.
**Files**: 5 YAML files (career learnings, maritime cases, mooring failures, naval resources)
**Page type**: Sources (reference summaries)
**Ingest rule**: Extract key themes and create source summary pages. Domain-specific content links to domain wikis.

## Incremental Ingest Conventions

1. **New source** → place raw file in `raw/<class>/`, run ingest, pages created automatically
2. **Updated source** → re-ingest; existing pages get `last_updated` bumped, new facts appended
3. **Duplicate detection** → before creating a page, check index.md for existing coverage
4. **Cross-wiki links** → when a page references marine/maritime/naval content, add `[[wiki:domain/page]]` links
5. **Log everything** → every ingest appends to `wiki/log.md`

### Class 6: Career Knowledge Seeds (`knowledge/seeds/career-learnings.yaml`)
**Priority**: High — 23 years of domain expertise in structured YAML.
**Files**: 11 entries across engineering (5), software (3), finance (1), drilling (1), energy (1)
**Page type**: Concepts (one per engineering topic)
**Ingest rule**: Extract context and patterns, create concept page with standards references and cross-refs.
**Status**: Ingested 2026-04-08 — 10 concept pages created (7 engineering + 3 software)

### Class 7: Dark Intelligence Extractions (`knowledge/dark-intelligence/`)
**Priority**: Medium — extracted engineering calculations from legacy Excel.
**Files**: 6 xlsx-poc extractions + 1 geotechnical extraction
**Page type**: Concepts (calculation methodology)
**Ingest rule**: Extract equations, inputs, methodology; create concept page with formulas and typical ranges.
**Status**: Ingested 2026-04-08 — 2 concept pages created (pile-capacity, sn-curve)

### Class 8: Session Memory / Solver Lessons (`.claude/memory/KNOWLEDGE.md`)
**Priority**: High — hard-won debugging patterns and tool usage.
**Page type**: Entities (tools) + Workflows (debugging protocols)
**Ingest rule**: Extract tool-specific patterns into entity pages; debugging protocols into workflow pages.
**Status**: Ingested 2026-04-08 — 3 entity pages + 2 workflow pages created

### Class 9: Skills Metadata (`.claude/skills/engineering/`)
**Priority**: Medium — engineering domain knowledge encoded in skill definitions.
**Files**: 96 markdown files across marine-offshore, CFD, CAD, drilling, GIS, standards domains
**Page type**: Entities (tools/systems) + Concepts (analysis methods)
**Ingest rule**: Read skill SKILL.md, extract domain knowledge, create entity or concept page. Group related sub-skills into single pages.
**Status**: Ingested 2026-04-09 — 9 pages created (4 entities + 5 concepts) from highest-value skills

### Class 10: Mooring Failures Seed (`knowledge/seeds/mooring-failures-lng-terminals.yaml`)
**Priority**: High — 40-entry curated knowledge base of mooring line failure incidents and standards.
**Files**: 1 YAML file with 40 entries (incidents, investigations, technical papers, standards)
**Page type**: Entities (specific incidents) + Concepts (failure physics) + Standards
**Ingest rule**: Group related entries into thematic pages. Create entity pages for major incidents, concept page for failure mechanisms, standards pages for key references.
**Status**: Ingested 2026-04-09 — 7 pages created (4 entities + 1 concept + 2 standards)

### Class 11: Closed Engineering Issues (GitHub `cat:engineering`)
**Priority**: Medium — key decisions and implementation approaches from completed work.
**Files**: 20 closed issues with `cat:engineering` label
**Page type**: Concepts (methodologies) + Workflows (pipelines)
**Ingest rule**: Extract architectural decisions, implementation patterns, and clean-room approaches. Focus on issues with the most instructive content.
**Status**: Ingested 2026-04-09 — 3 pages created from 5 issues (2 concepts + 1 workflow)

### Class 12: Research Outputs (`.planning/research/`)
**Priority**: Low — nightly researcher outputs, mostly software-focused.
**Files**: 12+ markdown reports across 6 domains (standards, python-ecosystem, ai-tooling, etc.)
**Page type**: Concepts (standards tracking)
**Ingest rule**: Only ingest engineering-specific content (standards domain). Other domains are software/AI-focused.
**Status**: Ingested 2026-04-09 — 1 concept page from 2 standards reports

## Future Source Classes (not yet ingested)

- Overnight batch run reports
- Additional closed engineering issues (15 remaining)
- Additional skill sub-skills (48 OrcaFlex sub-skills, AQWA sub-skills, etc.)
- Additional mooring failure seed entries (33 remaining entries without dedicated pages)
