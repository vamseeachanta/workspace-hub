# Terminal 2 — ANSYS Package TDD Expansion
# Provider: Codex seat 1 (bounded TDD implementation)
# Issues: #1676 (P0 ansys expansion)
# Est. Time: 2-3 hours

We are in /mnt/local-analysis/workspace-hub. This is a Python monorepo with
`digitalmodel/` as a nested git repo (separate .git). All commits for
digitalmodel code MUST be made from inside `digitalmodel/`.

Use `uv run` for all Python — never bare `python3` or `pip`.
Do NOT ask the user any questions. Work autonomously.
Do NOT branch — commit to `main` and push after each task.
Run `git pull origin main --rebase` before every push (stash if needed).
TDD mandatory: write tests BEFORE implementation.
Mock all external dependencies — do NOT require network, licenses, ANSYS installation, or mounts.

IMPORTANT: Do NOT write to any of these paths (owned by other terminals):
- digitalmodel/src/digitalmodel/cathodic_protection/ (Terminal 1)
- digitalmodel/tests/cathodic_protection/ (Terminal 1)
- digitalmodel/src/digitalmodel/fatigue/ (Terminal 3)
- digitalmodel/tests/fatigue/ (Terminal 3)
- digitalmodel/src/digitalmodel/solvers/ (Terminal 5)
- digitalmodel/src/digitalmodel/web/ (Terminal 4)
- digitalmodel/src/digitalmodel/reservoir/ (Terminal 4)
- scripts/solver/ (Terminal 5)
- scripts/document-intelligence/ (Terminal 4)

Only write to:
- digitalmodel/src/digitalmodel/ansys/
- digitalmodel/tests/ansys/

---

## TASK 1: ANSYS — Pressure Vessel Analysis Template (TDD)
GH Issue: #1676 (P0 — ansys expansion, ASME VIII template)

The ansys package has 14 source files but only 3 test files (test_apdl_reader,
test_design_points, test_wbjn_reader). Market signal: 249 FEA jobs. P0 priority.

### Existing source files to review first:
- digitalmodel/src/digitalmodel/ansys/pressure_vessel.py (already exists — review and extend)
- digitalmodel/src/digitalmodel/ansys/apdl_generator.py
- digitalmodel/src/digitalmodel/ansys/batch_runner.py
- digitalmodel/src/digitalmodel/ansys/models.py

### Implementation:
1. Read existing pressure_vessel.py to understand current state
2. Write tests: `digitalmodel/tests/ansys/test_pressure_vessel.py`
   - Test cylindrical shell thickness calc per ASME VIII Div 1
   - Test nozzle reinforcement check
   - Test hydrostatic test pressure calculation
   - Test MAWP calculation
   - Test APDL snippet generation for pressure load cases
   - At least 8 test cases
3. Extend pressure_vessel.py (or create if stub):
   - `PressureVesselInput` Pydantic model (diameter, length, pressure, material, temperature)
   - `calculate_shell_thickness(input) -> ShellResult`
   - `check_nozzle_reinforcement(nozzle, shell) -> ReinforcementResult`
   - `calculate_mawp(geometry, material) -> float`
   - `generate_pv_apdl(input) -> str` — APDL macro for pressure vessel FEA
4. Verify: `cd digitalmodel && uv run pytest tests/ansys/test_pressure_vessel.py -v`

Commit message: `feat(ansys): pressure vessel ASME VIII analysis template — TDD (#1676)`

---

## TASK 2: ANSYS — Batch Run Manager (TDD)
GH Issue: #1676 (P0 — batch run manager for multiple load cases)

### Implementation:
1. Read existing batch_runner.py to understand current state
2. Write tests: `digitalmodel/tests/ansys/test_batch_runner.py`
   - Test load case configuration parsing (YAML → BatchConfig)
   - Test APDL script generation for N load cases
   - Test results collection from mock output directories
   - Test summary report generation (CSV/JSON)
   - Test failure handling when a case fails
   - At least 8 test cases
3. Extend/implement batch_runner.py:
   - `BatchConfig` Pydantic model (base_model, load_cases: list, output_dir)
   - `LoadCase` model (name, loads: dict, boundary_conditions: dict)
   - `generate_batch_scripts(config: BatchConfig) -> list[Path]`
   - `collect_results(output_dir) -> BatchResults`
   - `generate_summary(results: BatchResults) -> str`
4. Verify: `cd digitalmodel && uv run pytest tests/ansys/test_batch_runner.py -v`

Commit message: `feat(ansys): batch run manager for multi-load-case FEA — TDD (#1676)`

---

## TASK 3: ANSYS — Results Extractor (TDD)
GH Issue: #1676 (P0 — results extractor: stress, displacement, reaction forces)

### Implementation:
1. Write tests: `digitalmodel/tests/ansys/test_results_extractor.py`
   - Test parsing ANSYS result summary text files (mock format)
   - Test extraction of max stress, max displacement, reaction forces
   - Test node/element result tabulation
   - Test JSON/CSV export of extracted results
   - Test multi-load-case results comparison
   - At least 6 test cases
2. Implement: `digitalmodel/src/digitalmodel/ansys/results_extractor.py`
   - `parse_result_file(path: Path) -> ANSYSResults`
   - `extract_stress_summary(results) -> StressSummary`
   - `extract_displacements(results) -> DisplacementSummary`
   - `compare_load_cases(results: list[ANSYSResults]) -> ComparisonTable`
   - `export_results(results, format='json') -> str`
3. Update `digitalmodel/src/digitalmodel/ansys/__init__.py` exports
4. Verify all ansys tests: `cd digitalmodel && uv run pytest tests/ansys/ -v`

Commit message: `feat(ansys): results extractor for stress/displacement/reactions — TDD (#1676)`

---

After all tasks, post a brief progress comment on GH issue #1676:
```
gh issue comment 1676 --repo vamseeachanta/workspace-hub --body "Terminal 2 overnight (2026-04-02): ansys P0 expansion complete.
- Extended pressure_vessel.py with ASME VIII calcs
- Extended batch_runner.py with multi-load-case management
- Added results_extractor.py for post-processing
- All with TDD: 22+ new test cases
ANSYS package: 14 modules → 14+ modules (extended), 3 test files → 6 test files"
```
