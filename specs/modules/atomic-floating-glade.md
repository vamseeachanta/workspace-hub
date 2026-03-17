# WRK-1279: Extract Numerical Test Vectors from Naval Architecture Literature

## Context

The digitalmodel repo has 15+ engineering domains with varying test coverage. Some domains (CP, fatigue, asset integrity) have rich inline test data in Python files but lack standardized YAML fixture files. Other domains (mooring, drilling, metocean) have almost no extracted test vectors. This feature systematically extracts input→output numerical data from standards, textbooks, and dark intelligence into a canonical YAML fixture format, enabling TDD for all future implementation WRKs.

## Approach

**Extract, don't create.** Each child reads existing test files and reference documents, then outputs standardized YAML fixture files following the dark-intelligence schema (`config/schemas/dark-intelligence-archive.yaml`). No new calculation code is written — only fixture YAML files.

### Fixture Schema

Use the established dark-intelligence YAML schema with these required fields per vector:

```yaml
source_type: standard | textbook | excel | python
source_description: "DNV-RP-B401 Table 10-2 — anode mass calc"
standard_ref: "DNV-RP-B401:2017 §10.2.1"
inputs:
  - name: "Current density"
    symbol: "i_c"
    unit: "mA/m²"
    test_value: 150.0
outputs:
  - name: "Anode mass"
    symbol: "M_a"
    unit: "kg"
    test_expected: 245.3
    tolerance: 0.5
use_as_test: true
```

### Output Location

```
digitalmodel/tests/fixtures/test_vectors/
  cathodic_protection/    # child-a
  fatigue/                # child-b
  naval_architecture/     # child-c
  hydrodynamics/          # child-d
  viv_pipeline_subsea/    # child-e
  structural/             # child-f
  mooring_risers/         # child-g
  drilling/               # child-h
  metocean_diffraction/   # child-i
  document_intelligence/  # child-doc (index YAML, not fixtures)
```

## Decomposition

10 children (consolidated from original 12 based on resource intelligence). All independent — full parallel execution.

### child-a: Cathodic Protection Test Vectors
- **Scope:** Extract from 19 existing test files (4,938 lines) + 4 source modules
- **Sources:** DNV-RP-B401, API RP 1632, ISO 15589-2, ABS GN, NACE
- **entry_reads:** `digitalmodel/tests/cathodic_protection/`, `digitalmodel/tests/specialized/cathodic_protection/`, `digitalmodel/src/digitalmodel/cathodic_protection/`
- **Target:** ≥15 vectors (richest domain — many already doc-verified)
- **orchestrator:** claude
- **blocked_by:** none

### child-b: Fatigue Test Vectors
- **Scope:** Extract from `worked_examples.py` (713 lines, 3 canonical cases) + 6 test files (6,310 lines)
- **Sources:** DNV-RP-C203, DNV-OS-E301, Palmgren-Miner
- **entry_reads:** `digitalmodel/src/digitalmodel/structural/fatigue/worked_examples.py`, `digitalmodel/tests/structural/fatigue/`
- **Target:** ≥10 vectors (S-N curves, damage accumulation, SCF)
- **orchestrator:** claude
- **blocked_by:** none

### child-c: Naval Architecture Test Vectors
- **Scope:** Extract from EN400 textbook examples (24 tests, 327 lines) + stability/hydrostatics modules
- **Sources:** USNA EN400 Principles of Ship Performance, WRK-1148 output (propeller-rudder literature)
- **entry_reads:** `digitalmodel/tests/naval_architecture/test_en400_worked_examples.py`, `digitalmodel/src/digitalmodel/naval_architecture/`, `.claude/work-queue/assets/WRK-1148/`
- **Target:** ≥15 vectors (textbook-verified — highest confidence)
- **orchestrator:** claude
- **blocked_by:** none

### child-d: Hydrodynamics Test Vectors
- **Scope:** Extract from passing ship benchmarks (6 files, 4,782 lines) + diffraction fixtures (3 YAML specs) + BEMRosetta
- **Sources:** Wang paper, Mathcad validation, AQWA vessel specs
- **entry_reads:** `digitalmodel/tests/hydrodynamics/passing_ship/`, `digitalmodel/tests/hydrodynamics/diffraction/fixtures/`, `digitalmodel/tests/hydrodynamics/bemrosetta/`
- **Target:** ≥15 vectors
- **orchestrator:** claude
- **blocked_by:** none

### child-e: VIV + Pipeline + Subsea Test Vectors
- **Scope:** VIV analysis (1,075 lines) + pipeline tests (12 files) + subsea
- **Sources:** DNV-RP-F105, DNV-OS-F101, API RP 1111
- **entry_reads:** `digitalmodel/tests/subsea/viv_analysis/`, `digitalmodel/tests/subsea/pipeline/`, `digitalmodel/src/digitalmodel/subsea/`
- **Target:** ≥15 vectors
- **orchestrator:** claude
- **blocked_by:** none

### child-f: Structural + Asset Integrity Test Vectors
- **Scope:** API 579 fixtures (40+ YAML configs) + fracture mechanics (28+ configs) + structural modules
- **Sources:** API 579, fracture mechanics, DNV CN 30.1
- **entry_reads:** `digitalmodel/tests/asset_integrity/test_data/`, `digitalmodel/src/digitalmodel/structural/`
- **Target:** ≥15 vectors (many already in YAML — reformat to canonical schema)
- **orchestrator:** claude
- **blocked_by:** none

### child-g: Mooring + Risers Test Vectors
- **Scope:** Extract from OrcaFlex references (67 mentions across codebase), API RP 2SK catenary, OCIMF
- **Sources:** OrcaFlex C05/C06/A05 examples, API RP 2SK, catenary geometry
- **entry_reads:** `digitalmodel/src/digitalmodel/mooring/`, `digitalmodel/tests/` (grep OrcaFlex)
- **Target:** ≥10 vectors (sparser domain — may need document index queries)
- **orchestrator:** claude
- **blocked_by:** none

### child-h: Drilling Test Vectors
- **Scope:** Torque & drag, casing burst/collapse/tension, mud weight, API 16Q stackup
- **Sources:** API 16Q, drilling engineering textbooks
- **entry_reads:** `digitalmodel/src/digitalmodel/drilling/` (if exists), dark intelligence PoC files
- **Target:** ≥10 vectors
- **orchestrator:** claude
- **blocked_by:** none

### child-i: Metocean + Diffraction Test Vectors
- **Scope:** JONSWAP spectrum parameters, NDBC station data, return periods, AQWA 6-DOF RAOs
- **Sources:** DNV-RP-C205, AQWA examples, wave spectrum theory
- **entry_reads:** `digitalmodel/src/digitalmodel/metocean/` (if exists), `digitalmodel/tests/hydrodynamics/diffraction/`
- **Target:** ≥10 vectors
- **orchestrator:** claude
- **blocked_by:** none

### child-doc: Document Intelligence Catalogue
- **Scope:** Query document index scripts for high-value documents not yet in repo across ≥5 domains
- **Sources:** `scripts/data/document-index/` pipeline (Phases A-G)
- **entry_reads:** `scripts/data/document-index/`, `config/schemas/dark-intelligence-archive.yaml`
- **Target:** Catalogue of ≥20 high-value documents with domain, standard number, availability status
- **Output:** `digitalmodel/tests/fixtures/test_vectors/document_intelligence/high-value-sources.yaml`
- **orchestrator:** claude
- **blocked_by:** none

## Shared Parameters Registry

Create `digitalmodel/tests/fixtures/test_vectors/shared_parameters.yaml` listing cross-domain constants:
- Seawater density (1025 kg/m³)
- Gravity (9.80665 m/s²)
- Steel yield stress (355 MPa typical)
- Cd/Cm drag/inertia coefficients
- Kinematic viscosity of seawater

Each child references this file rather than duplicating constants.

## Acceptance Criteria

- [ ] ≥200 total test vectors across all children
- [ ] Each vector: source_type, standard_ref, inputs (with units), outputs (with tolerance), use_as_test flag
- [ ] ≥10 vectors per HIGH-priority domain (CP, fatigue, naval arch, hydrodynamics, VIV+pipeline)
- [ ] ≥5 vectors per MEDIUM-priority domain (structural, mooring, drilling, metocean)
- [ ] Document index queried for ≥5 domains; high-value sources catalogued
- [ ] Dark intelligence entries with `use_as_test: true` incorporated
- [ ] All fixture YAML files validate against `config/schemas/dark-intelligence-archive.yaml`
- [ ] `shared_parameters.yaml` created with cross-domain constants
- [ ] pytest parametrize compatibility verified (at least 1 domain has a working parametrized test)

## Verification

```bash
# Validate all fixture files against schema
uv run --no-project python -c "
import yaml, pathlib, sys
schema_fields = ['source_type','source_description','inputs','outputs']
fixtures = pathlib.Path('digitalmodel/tests/fixtures/test_vectors').rglob('*.yaml')
count = 0
for f in fixtures:
    data = yaml.safe_load(f.read_text())
    if isinstance(data, list):
        count += len(data)
    else:
        count += 1
print(f'Total vectors: {count}')
sys.exit(0 if count >= 200 else 1)
"

# Run existing tests to confirm no breakage
cd digitalmodel && PYTHONPATH=src uv run python -m pytest tests/ -x -q
```

## Key Files

| Purpose | Path |
|---------|------|
| Fixture schema | `config/schemas/dark-intelligence-archive.yaml` |
| Fixture output root | `digitalmodel/tests/fixtures/test_vectors/` |
| CP source tests | `digitalmodel/tests/cathodic_protection/` + `tests/specialized/cathodic_protection/` |
| Fatigue worked examples | `digitalmodel/src/digitalmodel/structural/fatigue/worked_examples.py` |
| Naval arch textbook tests | `digitalmodel/tests/naval_architecture/test_en400_worked_examples.py` |
| Passing ship benchmarks | `digitalmodel/tests/hydrodynamics/passing_ship/` |
| VIV + pipeline tests | `digitalmodel/tests/subsea/` |
| Asset integrity fixtures | `digitalmodel/tests/asset_integrity/test_data/` |
| Dark intelligence example | `knowledge/dark-intelligence/geotechnical/pile_capacity/` |
| Document index scripts | `scripts/data/document-index/` |
| WRK-1148 evidence | `.claude/work-queue/assets/WRK-1148/` |
