# Data Intelligence — Registry & Index Map

> Quick reference: where all data registries, indexes, catalogs, and intelligence artifacts live across the workspace-hub ecosystem. Consult this before searching.

---

## 1. Document Intelligence (extraction pipeline)

| What | Location | Notes |
|------|----------|-------|
| **Corpus index** | `data/document-index/index.jsonl` | 1,033,933 records with domain, target_repos, status, org, readability |
| **Registry stats** | `data/document-index/registry.yaml` | Counts by source (6), domain (12), repo (11) |
| **Summaries** | `data/document-index/summaries/<sha>.json` | Per-document LLM/deterministic classification (639K done) |
| **Standards ledger** | `data/document-index/standards-transfer-ledger.yaml` | 425 standards → repo/module mapping. Done: 29, Gap: 235 |
| **Mounted sources** | `data/document-index/mounted-source-registry.yaml` | 7 source definitions (local, remote, API) |
| **Checkpoints** | `data/document-index/checkpoints/` | Batch progress snapshots |
| **Data audit** | `data/document-index/data-audit-report.md` | Phase B enrichment status |
| **Maturity tracking** | `data/document-index/resource-intelligence-maturity.yaml` | Docs read, calculations implemented, follow-up WRKs |

### Structured Extracts (Phase B output)

| File | Records | Content |
|------|---------|---------|
| `data/doc-intelligence/requirements.jsonl` | 12.0M | Extracted requirements |
| `data/doc-intelligence/constants.jsonl` | 4.9M | Engineering constants |
| `data/doc-intelligence/equations.jsonl` | 2.0M | Equations |
| `data/doc-intelligence/procedures.jsonl` | 1.4M | Procedures |
| `data/doc-intelligence/definitions.jsonl` | 717K | Definitions |
| `data/doc-intelligence/worked_examples.jsonl` | 279K | Worked examples |

### Deep Extraction Artifacts

| What | Location | Notes |
|------|----------|-------|
| **Tables** | `data/doc-intelligence/deep/tables/<domain>/` | cathodic-protection, fatigue, marine, mooring, pipeline, structural |
| **Charts** | `data/doc-intelligence/deep/charts/<domain>/` | Same domains |
| **Extraction reports** | `data/doc-intelligence/extraction-reports/naval-architecture/` | 44 YAML reports for textbooks/standards |
| **Deep reports** | `data/doc-intelligence/deep/` | 9 reports (API 579-1, DNV RP series, ISO) |
| **Manifest index** | `data/doc-intelligence/manifest-index.jsonl` | Cross-reference of all extraction manifests |
| **Table quality audit** | `data/doc-intelligence/table-quality-audit.yaml` | Extraction quality assessment |

### Domain Catalogs

| What | Location | Notes |
|------|----------|-------|
| **Naval architecture** | `data/doc-intelligence/naval-architecture-catalog.yaml` | 144 docs, 110 ship plans, 21 textbooks, 65 hull codes |
| **Ship plans index** | `data/doc-intelligence/ship-plans-index.yaml` | By hull code and vessel category |
| **EN400 worked examples** | `data/doc-intelligence/en400-worked-examples.yaml` | USNA stability textbook extracts |

### Skills & Scripts

| Skill | Path | Use when |
|-------|------|----------|
| `document-index-pipeline` | `.claude/skills/data/document-index-pipeline/SKILL.md` | 7-phase A→G batch pipeline |
| `doc-intelligence-promotion` | `.claude/skills/data/doc-intelligence-promotion/SKILL.md` | Single-doc extraction + post-processing |

Scripts: `scripts/data/document-index/` — 16 scripts, 88% deterministic.

---

## 2. Research Literature (downloaded papers & standards)

| What | Location | Notes |
|------|----------|-------|
| **Literature store** | `/mnt/ace-data/digitalmodel/docs/domains/<domain>/literature/` | PDFs by domain and subtopic |
| **Domain-repo mapping** | `config/research-literature/domain-repo-map.yaml` | 12 domains, Tier 1-3 priority classification |
| **Mount** | `/mnt/ace-data` → `/mnt/ace` (local `/dev/sda1` on ace-linux-1) | 7.5TB, NFS-shared rw to ace-linux-2 |
| **Download scripts** | `<domain>/literature/download-literature.sh` per domain | Reproducible acquisition with source URLs |

### Domains

cathodic_protection, geotechnical, hydrodynamics, naval_architecture, pipeline, structural, structural-parachute, subsea

### Access

- **ace-linux-1**: local drive, always available
- **ace-linux-2**: NFS mount at `/mnt/remote/ace-linux-1/ace` (rw, setup via `scripts/setup/nfs-ace-drive.sh`)

---

## 3. Dark Intelligence (private legacy extraction)

| What | Location | Notes |
|------|----------|-------|
| **Archive** | `knowledge/dark-intelligence/` | Gitignored YAMLs; only README tracked |
| **Schema** | `config/schemas/dark-intelligence-archive.yaml` | Validation schema |
| **Tests** | `tests/skills/test_dark_intelligence_schema.py` | Schema + workflow validation |
| **POC extractions** | `knowledge/dark-intelligence/xlsx-poc/` | 8+ proof-of-concept spreadsheet extractions |

### Skills

| Skill | Path | Use when |
|-------|------|----------|
| `dark-intelligence-workflow` | `.claude/skills/data/dark-intelligence-workflow/SKILL.md` | Porting legacy Excel → clean, client-free implementations |

---

## 4. Per-Repo Data Registries

| Repo | Asset | Location |
|------|-------|----------|
| **digitalmodel** | Data-needs registry | `digitalmodel/specs/data-needs.yaml` — lifecycle-tracked entries across all domains |
| **digitalmodel** | External data sources | `digitalmodel/config/data_sources.yaml` — Tier 1-2 dependencies on worldenergydata |
| **digitalmodel** | Shared GZ corpus | `digitalmodel/data/doc-intelligence/digitized-curves/gz-curves.yaml` |
| **worldenergydata** | Data catalog | `worldenergydata/data/catalog/data-catalog.yml` — 246 datasets, 10 modules |
| **worldenergydata** | API contracts | `worldenergydata/docs/api-contracts.md` |
| **workspace-hub** | Per-repo data source specs | `.planning/archive/data-sources/<repo>.yaml` — 9 repos covered |

---

## 5. Standards & Reference Data

| What | Location | Notes |
|------|----------|-------|
| **Design code registry** | `data/design-codes/code-registry.yaml` | 30+ codes (DNV, API, ASTM, ISO, BS), edition tracking, current/check/superseded |
| **Online resources** | `.planning/archive/online-resources/catalog.yaml` | 50+ evaluated resources (The Well, DNV explorer, API portal) |
| **Capability maps** | `.planning/archive/capability-map/` | Module-to-standards mappings |
| **Research briefs** | `.planning/archive/capability-map/research-briefs/` | 13 domain expertise summaries |
| **Public data sources** | `data/document-index/public-og-data-sources.yaml` | Public O&G data sources |
| **Domain coverage** | `docs/document-intelligence/domain-coverage.md` | Standards coverage by domain |

---

## 6. Knowledge Seeds

| What | Location | Notes |
|------|----------|-------|
| **Career learnings** | `knowledge/seeds/career-learnings.yaml` | Engineering experience knowledge |
| **Maritime law** | `knowledge/seeds/maritime-law-cases.yaml` | Legal case references |
| **Maritime liabilities** | `knowledge/seeds/maritime-liabilities.yaml` | Liability frameworks |
| **Naval architecture resources** | `knowledge/seeds/naval-architecture-resources.yaml` | Domain resources |
| **Schema** | `knowledge/seeds/schema.md` | Seed format specification |

---

## 7. Governance & Quality

| What | Location | Notes |
|------|----------|-------|
| **Data residence policy** | `docs/DATA_RESIDENCE_POLICY.md` | 3-tier model (ADR-004) |
| **Compliance config** | `config/data-residence-compliance.yaml` | ADR-004 enforcement |
| **Quality gap report** | `config/quality/quality-gap-report.yaml` | Workspace-wide assessment |
| **Coverage baseline** | `config/testing/coverage-baseline.yaml` | Test coverage targets |
| **Resource intelligence template** | `.claude/skills/workspace-hub/resource-intelligence/templates/` | Gate-checked schema for WRK assessments |

---

## 7. Mount Drive Knowledge Maps (2026-04-02)

| What | Location | Notes |
|------|----------|-------|
| **Mount drive knowledge map** | `docs/document-intelligence/mount-drive-knowledge-map.md` | Complete catalog of all 4 mount points, 3.6M+ files, search guides |
| **DDE remote drive catalog** | `docs/document-intelligence/dde-drive-catalog.md` | First inventory of DDE (2.8TB) — 18 missing standards orgs, MATLAB code, unique projects |
| **Gap closure action plan** | `docs/document-intelligence/resource-intelligence-action-plan.md` | P0-P3 prioritized actions: conference indexing, DDE registration, standards migration |
| **Undiscovered resources** | `docs/reports/ace-undiscovered-resources.md` | Top 20 unindexed resources ranked by value |
| **Mounted source registry** | `data/document-index/mounted-source-registry.yaml` | 8 sources defined (DDE needs 3 more) |

### Key Gaps Identified

- **38,526 conference papers** in `/mnt/ace/docs/conferences/` — 0% indexed (OMAE, OTC, DOT, ISOPE)
- **DDE remote drive** — not in pipeline, contains 18 standards orgs missing from /mnt/ace
- **Standards ledger** — only 425 of 26,884 files on disk (1.6%)

---

## Cross-References

- **index.jsonl** `target_repos` field links documents → repos; `domain` links → engineering domains
- **standards-transfer-ledger** maps standards → repo + module + implementation status
- **data-needs.yaml** entries point to both `doc-intelligence/` artifacts and `tests/fixtures/test_vectors/` fixtures
- **domain-repo-map.yaml** links research literature domains → target repos
- **capability-map** links modules → standards they implement
- Dark intelligence → public repos via 6-step workflow; document intelligence → via 7-phase pipeline
- Both pipelines share `doc-intelligence-promotion` for post-processing
- **mount-drive-knowledge-map.md** — "Where is...?" quick reference for all resource types
- **dde-drive-catalog.md** — detailed DDE inventory with migration recommendations
