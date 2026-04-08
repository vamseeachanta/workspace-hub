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

## Future Source Classes (not yet ingested)

- Skill metadata (`.claude/skills/`) — 691+ skills, each could become a wiki page
- GitHub issue knowledge (closed engineering issues)
- Overnight batch run reports
- Research outputs (`.planning/research/`)
- Mooring failures seed (`knowledge/seeds/mooring-failures-lng-terminals.yaml`) — 40 entries
