# Terminal 2 — Codex Seat 1 — OrcaWave Test Coverage + Pipeline TDD

We are in /mnt/local-analysis/workspace-hub. Execute these 3 tasks in order.
Use `uv run` for all Python — never bare `python3` or `pip`.
Commit to main and push after each task. Do not branch.
Run `git pull origin main` before every push.
TDD: write tests BEFORE implementation.
Do NOT ask the user any questions — make reasonable decisions and document them.

## TASK 1: OrcaWave Package Test Suite (GH #1585)

### Context
The orcawave package at digitalmodel/src/digitalmodel/orcawave/ has 13 source files and 0 tests.
Key classes: OrcaWaveReportBuilder, SectionConfig, ModelSummaryConfig, RAOPlotsConfig,
HydroMatricesConfig, and 6+ more config models.
Existing spec.yml fixtures live somewhere under the repo (L00-L04 cases).
The package is SKELETON status — needs to move to DEVELOPMENT (requires ≥1 test file).

### What to do
1. Read ALL 13 source files under digitalmodel/src/digitalmodel/orcawave/ to understand the API
2. Create test directory: digitalmodel/tests/orcawave/
3. Write test files:
   - digitalmodel/tests/orcawave/test_report_builder.py — test OrcaWaveReportBuilder init, section generation
   - digitalmodel/tests/orcawave/test_config_models.py — test all Pydantic config models with valid/invalid data
   - digitalmodel/tests/orcawave/test_spec_validation.py — validate spec.yml files against the schema
   - digitalmodel/tests/orcawave/__init__.py
4. Tests should use pytest fixtures, parametrize where applicable
5. Tests should NOT require actual OrcaWave solver — mock external dependencies
6. Run tests: `uv run pytest digitalmodel/tests/orcawave/ -v`

### Acceptance criteria
- At least 3 test files in digitalmodel/tests/orcawave/
- At least 15 test functions total
- All tests pass (no actual solver needed)
- Tests cover config model validation (valid + invalid inputs)
- Package moves from SKELETON to DEVELOPMENT

### Commit message
test(orcawave): add test suite for orcawave package — SKELETON → DEVELOPMENT (#1585)

---

## TASK 2: Parametric Spec Generator Tests (GH #1596)

### Context
Issue #1596 wants a parametric spec.yml generator that creates DiffractionSpec-compliant
spec files from sweep definitions. The DiffractionSpec schema is defined in
digitalmodel/src/digitalmodel/specs/input_schemas.py (789 lines of Pydantic v2 models).
Existing spec.yml files (L00-L04) show the expected output format.

### What to do
1. Read digitalmodel/src/digitalmodel/specs/input_schemas.py to understand the DiffractionSpec schema
2. Find and read 2-3 existing spec.yml files to understand the concrete format
3. Write tests first in digitalmodel/tests/solver/test_parametric_spec_generator.py:
   - test_single_spec_generation — generate one spec from known parameters
   - test_frequency_sweep — parametric sweep over frequency ranges
   - test_heading_sweep — parametric sweep over wave headings
   - test_hull_parameter_sweep — vary hull dimensions
   - test_spec_schema_compliance — generated specs validate against DiffractionSpec
4. Then implement a minimal generator in digitalmodel/src/digitalmodel/solvers/parametric_spec_generator.py
5. Run: `uv run pytest digitalmodel/tests/solver/test_parametric_spec_generator.py -v`

### Acceptance criteria
- Test file exists at digitalmodel/tests/solver/test_parametric_spec_generator.py
- At least 5 test functions
- Generator exists at digitalmodel/src/digitalmodel/solvers/parametric_spec_generator.py
- Generated specs validate against DiffractionSpec Pydantic model
- All tests pass

### Commit message
feat(solver): parametric spec.yml generator with TDD test suite (#1596)

---

## TASK 3: DiffractionSpec Pipeline Integration Test (GH #1598)

### Context
Issue #1598 wants an end-to-end integration test for the DiffractionSpec pipeline:
spec.yml → OrcaWaveBackend → native solver YAML.
The backend is in digitalmodel/src/digitalmodel/orcawave/ or digitalmodel/src/digitalmodel/solvers/.

### What to do
1. Find the OrcaWaveBackend class (search for it in the codebase)
2. Write digitalmodel/tests/solver/test_diffraction_pipeline_e2e.py:
   - test_spec_load_and_validate — load a real spec.yml, validate against schema
   - test_backend_initialization — create backend from spec
   - test_native_yaml_generation — backend produces solver-native YAML (mock solver)
   - test_round_trip — spec → backend → native YAML → parse back
3. Use existing L00 spec.yml as fixture data
4. Mock the actual solver call but verify the pipeline plumbing works

### Acceptance criteria
- Integration test file at digitalmodel/tests/solver/test_diffraction_pipeline_e2e.py
- At least 4 test functions
- Tests pass without requiring OrcaWave license
- Uses real spec.yml fixture data

### Commit message
test(solver): end-to-end DiffractionSpec pipeline integration test (#1598)

---

## After all tasks
Post a brief progress comment on each GitHub issue (#1585, #1596, #1598) in repo vamseeachanta/workspace-hub:
"Overnight agent run (2026-04-01): [artifact] committed. See [path]."
