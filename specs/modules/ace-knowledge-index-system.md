# ACE Knowledge Index System

> Organize 4.5TB of offshore engineering documents into an efficient, indexed knowledge system for humans and AI agents.

**Package home:** `aceengineer-admin` repo → `aceengineer_admin/knowledge/` subpackage
**Index location:** `/mnt/ace/.ace-knowledge/index.db` (SQLite, on NAS)
**Search:** FTS5 keyword search first, semantic embeddings later

---

## Problem

`/mnt/ace` contains ~1.45M files (4.5TB) across offshore/subsea engineering: standards, project reports, calculations, CAD, OrcaFlex simulations, Python/MATLAB code, and spreadsheets. Partially organized but no unified query layer. workspace-hub repos cannot discover or leverage this knowledge.

## Current State

| Asset | Location | Count | Status |
|-------|----------|-------|--------|
| O&G Standards | `/mnt/ace/O&G-Standards/` | 27,343 docs | Cataloged: `_catalog.json` + SQLite with 1M+ chunks & embeddings |
| Projects (9 disciplines) | `/mnt/ace/docs/disciplines/` | 137 projects | Migrated with README templates, `index_schema.csv` |
| OrcaFlex simulations | `/mnt/ace/_ss_repo/` | 5,799 .sim + .dat | Organized by project, no index |
| Python scripts | Scattered | 1,632 | No catalog, many use OrcFxAPI |
| MATLAB files | Scattered | 529 | No catalog |
| Jupyter notebooks | Scattered | 34 | No catalog |
| Excel calculations | Project `03_calcs/` folders | 27K+ xls/xlsx | No formula extraction |
| MRV Knowledge Base | `knowledge_skills/` | ~4 projects | ChromaDB RAG, limited scope |

---

## Solution: `aceengineer_admin.knowledge` Subpackage

Lives inside `aceengineer-admin` alongside `invoice/`, `tax/`, `common/`. Follows existing patterns: Click CLI, YAML config, setuptools, pytest.

### Package Structure

```
aceengineer-admin/                          # Existing repo
  aceengineer_admin/
    __init__.py                             # Existing
    cli.py                                  # Existing - add 'knowledge' group
    common/                                 # Existing
    invoice/                                # Existing
    tax/                                    # Existing
    knowledge/                              # NEW subpackage
      __init__.py
      schema.py                             # Pydantic/dataclass models
      config.py                             # Knowledge-specific config loader
      index/
        __init__.py
        unified_index.py                    # Main facade: AceKnowledgeIndex
        sqlite_backend.py                   # SQLite + FTS5 storage
        query_engine.py                     # Python API for agents
      scanners/
        __init__.py
        base.py                             # Abstract scanner interface
        standards_scanner.py                # Bridge existing _inventory.db
        project_scanner.py                  # Walk discipline/project tree
        code_scanner.py                     # Python/MATLAB/Jupyter via ast
        spreadsheet_scanner.py              # Excel formulas via openpyxl
        simulation_scanner.py               # OrcaFlex .dat metadata
      extractors/
        __init__.py
        base.py                             # Abstract extractor
        formula_extractor.py                # Math from Excel + code
        methodology_extractor.py            # Engineering procedures
        data_extractor.py                   # Material props, env conditions
        code_pattern_extractor.py           # Reusable code templates
      anonymizer/
        __init__.py
        project_anonymizer.py               # Strip client/field names
        rules.py                            # Anonymization rule config
      artifacts/
        __init__.py
        methodology_card.py                 # Generate methodology cards
        formula_library.py                  # Formula catalog
        reference_data.py                   # Reference data tables
        code_patterns.py                    # Reusable code patterns
        test_fixtures.py                    # Anonymized test data
  config/
    knowledge.yaml                          # NEW - knowledge config
    anonymization-rules.yaml                # NEW - client name patterns
  tests/
    knowledge/                              # NEW - knowledge tests
      __init__.py
      test_schema.py
      test_sqlite_backend.py
      test_standards_scanner.py
      test_project_scanner.py
      test_code_scanner.py
      test_query_engine.py
      test_anonymizer.py
      conftest.py                           # Fixtures for knowledge tests

/mnt/ace/.ace-knowledge/                    # On NAS (not git-tracked)
  index.db                                  # SQLite unified index
  backups/                                  # DB backups
  artifacts/                                # Generated cards, formulas, etc.
```

### CLI Integration

Add `knowledge` command group to existing `aceengineer_admin/cli.py`:

```bash
# Scanning
aceengineer knowledge scan --source standards    # Bridge O&G standards
aceengineer knowledge scan --source projects     # Catalog 137 projects
aceengineer knowledge scan --source code         # Index Python/MATLAB
aceengineer knowledge scan --all                 # Scan everything

# Querying
aceengineer knowledge search "drilling riser VIV"
aceengineer knowledge standard API RP 2RD
aceengineer knowledge formula --domain fatigue
aceengineer knowledge pattern --language python --domain orcaflex
aceengineer knowledge reference --category material_properties

# Status
aceengineer knowledge stats
aceengineer knowledge stats --report            # HTML coverage report
```

### Dependencies to Add

In `pyproject.toml`, add to existing `dependencies`:
```
"tqdm>=4.0"        # Progress bars for scanning
"rich>=13.0"       # Already in tech-stack, ensure present
```

Optional extra for semantic search (later):
```toml
[project.optional-dependencies]
knowledge-semantic = ["sentence-transformers>=2.2", "numpy>=1.24"]
```

Core deps already available: `openpyxl`, `PyPDF2`/`pypdf`, `pyyaml`, `click`, `pandas`.

---

## Index Schema (SQLite at `/mnt/ace/.ace-knowledge/index.db`)

### Core Tables

**`assets`** — Every indexable file:
| Column | Type | Purpose |
|--------|------|---------|
| id | TEXT PK | UUID or content-hash |
| asset_type | TEXT | 'document', 'code', 'spreadsheet', 'simulation', 'data' |
| file_path | TEXT UNIQUE | Absolute path on /mnt/ace |
| file_name | TEXT | Filename |
| file_extension | TEXT | .pdf, .py, etc. |
| file_size | INTEGER | Bytes |
| content_hash | TEXT | SHA-256 for dedup |
| modified_date | TEXT | ISO datetime |
| source_root | TEXT | '/mnt/ace/O&G-Standards', '/mnt/ace/docs/disciplines', etc. |
| discipline | TEXT | 'drilling', 'production', etc. (NULL for standards) |
| project_code | TEXT | '0113', '31290', etc. |
| folder_phase | TEXT | '00_inbox', '03_calcs', etc. |
| title | TEXT | Document title |
| description | TEXT | Summary |
| content_category | TEXT | 'standard', 'report', 'calculation', 'code', 'model', 'data' |
| engineering_domain | TEXT | 'fatigue', 'viv', 'mooring', 'riser', 'pipeline', etc. |
| scan_date | TEXT | When last scanned |
| extraction_status | TEXT | 'pending', 'extracted', 'skipped' |
| anonymized_title | TEXT | Title with client names stripped |

**`standards`** — Extended O&G standards metadata (FK → assets):
- organization, doc_type, doc_number, edition, year, superseded_by

**`formulas`** — Extracted equations (FK → assets):
- name, expression (LaTeX/symbolic), variables (JSON), domain, standard_reference, implementation_hint

**`methodologies`** — Engineering procedures:
- name, description, steps (JSON), inputs/outputs (JSON), standards_used, tools_used, domain

**`reference_data`** — Material properties, environmental data, unit conversions:
- category, name, data (JSON), units (JSON), source_standard

**`code_patterns`** — Reusable code templates (FK → assets):
- name, language, pattern_type, code_template, parameters (JSON), domain

**`cross_references`** — Links between assets:
- source_id, target_id, relationship ('references', 'implements', 'uses_data_from')

**`assets_fts`** — FTS5 virtual table over title, description, anonymized_title

**`asset_tags`** — Flexible tagging: asset_id, tag, tag_category

---

## Python API (for AI agents and workspace-hub code)

```python
from aceengineer_admin.knowledge import AceKnowledgeIndex

kb = AceKnowledgeIndex()

# Search
kb.search("drilling riser VIV analysis", top_k=10)

# Standards lookup
kb.find_standard("API", number="2RD")
kb.find_standard("DNV", doc_type="RP", number="C203")

# Formulas
kb.find_formulas(domain="fatigue", name="S-N curve")

# Methodologies
kb.find_methodology(domain="drilling", keywords=["riser", "global analysis"])

# Reference data
kb.get_reference_data("material_properties", "API 5L X65")
kb.get_reference_data("sn_curves", "DNV-RP-C203")
kb.get_reference_data("unit_conversions")

# Code patterns
kb.find_code_patterns(language="python", domain="orcaflex", pattern_type="batch_simulation")

# Cross-references
kb.get_related(asset_id="...")

# Stats
kb.stats()
```

---

## Anonymization Strategy

**Config:** `config/anonymization-rules.yaml`

```yaml
client_patterns:
  - pattern: '(?i)\b(shell|bp|ecopetrol|chevron|anadarko|eni|repsol|murphy|grupo.?r)\b'
    replacement: 'CLIENT'
  - pattern: '(?i)\b(prelude|macondo|perdido|stones|marlin|boreas|carcara|piklis)\b'
    replacement: 'FIELD'
  - pattern: '(?i)\b(cosl|disys|sta|tjg|fdas|tvo|bopt|rii|wcot|kbr)\b'
    replacement: 'CONTRACTOR'
```

- Real paths stored in `assets` (needed for human navigation)
- `anonymized_title` generated at scan time for AI-facing output
- Test fixtures use anonymized + scaled values (structure preserved, magnitudes changed)
- Project numbers kept (carry no client info alone)

---

## Implementation Phases

### Phase 1: Index Foundation + Scanning (parallel tracks)

**Track A — Standards Bridge:**
1. Create `knowledge/` subpackage skeleton with `__init__.py` files
2. Implement `schema.py` with Pydantic models for all entities
3. Implement `sqlite_backend.py` (table creation, CRUD, FTS5)
4. Implement `standards_scanner.py` — bridge existing `_inventory.db` (27,343 docs)
5. Implement `unified_index.py` + `query_engine.py`
6. Add `knowledge` group to `cli.py`
7. Tests: `test_schema.py`, `test_sqlite_backend.py`, `test_standards_scanner.py`

**Track B — Project + Code Scanning (parallel with Track A):**
1. Implement `project_scanner.py` — walk `docs/disciplines/*/projects/*/`
2. Implement `code_scanner.py` — parse Python with `ast`, MATLAB with regex
3. Implement `spreadsheet_scanner.py` — read sheet names, formula cells
4. Implement `simulation_scanner.py` — OrcaFlex `.dat` metadata extraction
5. Implement `project_anonymizer.py` with rules from YAML config
6. Tests: `test_project_scanner.py`, `test_code_scanner.py`, `test_anonymizer.py`

**Shared:**
- `config/knowledge.yaml` — source paths, file type mappings
- `config/anonymization-rules.yaml` — client/field/contractor patterns
- `pyproject.toml` updates — add `tqdm` dependency

**Files to create:**
- `aceengineer_admin/knowledge/__init__.py` (+ all subpackage `__init__.py`)
- `aceengineer_admin/knowledge/schema.py`
- `aceengineer_admin/knowledge/config.py`
- `aceengineer_admin/knowledge/index/unified_index.py`
- `aceengineer_admin/knowledge/index/sqlite_backend.py`
- `aceengineer_admin/knowledge/index/query_engine.py`
- `aceengineer_admin/knowledge/scanners/base.py`
- `aceengineer_admin/knowledge/scanners/standards_scanner.py`
- `aceengineer_admin/knowledge/scanners/project_scanner.py`
- `aceengineer_admin/knowledge/scanners/code_scanner.py`
- `aceengineer_admin/knowledge/scanners/spreadsheet_scanner.py`
- `aceengineer_admin/knowledge/scanners/simulation_scanner.py`
- `aceengineer_admin/knowledge/anonymizer/project_anonymizer.py`
- `aceengineer_admin/knowledge/anonymizer/rules.py`
- `config/knowledge.yaml`
- `config/anonymization-rules.yaml`
- `tests/knowledge/conftest.py`
- `tests/knowledge/test_schema.py`
- `tests/knowledge/test_sqlite_backend.py`
- `tests/knowledge/test_standards_scanner.py`
- `tests/knowledge/test_project_scanner.py`
- `tests/knowledge/test_code_scanner.py`
- `tests/knowledge/test_query_engine.py`
- `tests/knowledge/test_anonymizer.py`

**Files to modify:**
- `aceengineer_admin/cli.py` — add `@main.group() knowledge` commands
- `pyproject.toml` — add `tqdm` dependency, optional `knowledge-semantic` extra

**Result:** All 27,343 standards + 137 projects + 2,200 code files searchable via CLI and Python API

### Phase 2: Knowledge Extraction

**Deliverables:**
- `extractors/formula_extractor.py` — equations from Excel formulas + Python/MATLAB functions
- `extractors/methodology_extractor.py` — procedures from project READMEs, report structures
- `extractors/data_extractor.py` — material properties, env conditions, unit conversions
- `extractors/code_pattern_extractor.py` — OrcaFlex API patterns, FEA workflows, post-processing

**Priority extraction targets:**
- OrcaFlex API patterns (24+ scripts in `_ss_repo/0127/Python Programming/`)
- MATLAB calculations (wind speed, VIV, riser integrity in `data/va-hdd-2/`)
- Kriging interpolation notebook (`docs/disciplines/drilling/projects/0168_python_support/`)
- Unit conversions found across codebase (0.3048 m→ft, 0.145 Pa→psi, etc.)
- S-N curve parameters, pipe dimensions, steel grades from standards

**Result:** `formulas`, `methodologies`, `reference_data`, `code_patterns` tables populated

### Phase 3: Artifacts + Integration

**Deliverables:**
- `artifacts/methodology_card.py` — generate YAML/Markdown methodology cards
- `artifacts/formula_library.py` — categorized formula catalog
- `artifacts/reference_data.py` — exportable data tables (material props, S-N curves, metocean)
- `artifacts/code_patterns.py` — anonymized, generalized code templates
- `artifacts/test_fixtures.py` — generate pytest fixtures from anonymized project data
- Claude Code skill at `.claude/skills/eng/ace-knowledge.md`
- Integration with `digitalmodel` as optional dependency

**workspace-hub integration points:**
- `digitalmodel/fatigue/sn_curves.py` — reference data from index
- `digitalmodel/mooring/` — methodology cards for analysis templates
- Test suites import anonymized fixtures

**Result:** Full knowledge system operational and connected to workspace-hub

### Phase 4: Maintenance

**Deliverables:**
- Incremental scan: `aceengineer knowledge scan --incremental`
- Refresh stale entries: `aceengineer knowledge refresh`
- HTML coverage report: `aceengineer knowledge stats --report`
- Documentation

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Inside `aceengineer-admin` | User preference; follows existing module pattern (invoice, tax, knowledge) |
| SQLite + FTS5 (not vector DB) | Proven at scale with `_inventory.db` (1M+ rows). FTS5 handles 90% of queries. |
| Single `index.db` on NAS | Simple, co-located with data. Package code in git, index on `/mnt/ace`. |
| Bridge existing data | Don't re-extract 27K standards or 1M chunks — bridge the existing SQLite. |
| Anonymize at output time | Store real paths for navigation; strip names in generated artifacts only. |
| `ast` for Python parsing | Reliable without executing code; regex fallback for MATLAB. |
| Parallel Phase 1 tracks | Standards bridge is quick (data exists); project scanning can run simultaneously. |

---

## Verification

| Phase | Test |
|-------|------|
| 1A | `aceengineer knowledge stats` → 27,343 standards; `aceengineer knowledge search "API 2RD"` → correct results |
| 1B | `aceengineer knowledge stats` → 137 projects + 2,200 code files; `aceengineer knowledge search "drilling riser"` → project files |
| 2 | `aceengineer knowledge formula --domain fatigue` → S-N curve equations; methodology cards for major analysis types |
| 3 | `from aceengineer_admin.knowledge import AceKnowledgeIndex` works in digitalmodel; test fixtures pass pytest |
| 4 | Adding a file then `scan --incremental` picks it up; `stats --report` generates HTML |
| All | `uv run pytest tests/knowledge/ --cov=aceengineer_admin.knowledge` passes with 80%+ coverage |
