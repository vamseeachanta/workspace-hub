# WRK-149 Subagent Briefs (Low Codex Usage Mode)

## Claude Subagent Brief (Triage + Orchestration)
You are the Claude subagent for WRK-149 in `digitalmodel`.

### Objective
Triage remaining failures in the broad WRK-149 priority scope and produce a categorized remediation plan with minimal code churn.

### Scope Command
Use:
`uv run python -m pytest tests/hydrodynamics/hull_library tests/hydrodynamics/diffraction tests/structural/fatigue src/digitalmodel/asset_integrity/tests --cov=src/digitalmodel --cov-report=term --cov-report=xml:coverage.wrk149.priority.xml -q`

### Deliverables
1. Categorize failures into:
- environment/data dependency
- flaky/nondeterministic
- true regressions
- legacy expected failures
2. Propose skip/fixture/ownership policy per category.
3. Provide a prioritized list of 5-10 candidate fixes with estimated impact.
4. Do not refactor unrelated modules.

### Constraints
- Use `uv run` only.
- Preserve existing behavior unless issue is clearly a test hygiene defect.
- Avoid touching proprietary/license-gated solver paths.

---

## Gemini Subagent Brief (Coverage Expansion)
You are the Gemini subagent for WRK-149 in `digitalmodel`.

### Objective
Expand unit coverage for `asset_integrity/common/yml_utilities.py` from ~84.76% toward 90%+ with deterministic tests.

### Starting File
`src/digitalmodel/asset_integrity/tests/test_yml_utilities_additional.py`

### Targeted Remaining Areas
- uncovered branches around fallback/update exception paths
- `analyze_yaml_keys` output path
- `compare_yaml_files_deepdiff` diff branch with save hooks
- `get_library_yaml_file` local-file path branch

### Constraints
- Use `uv run` only.
- No network access.
- No broad-suite runs; keep commands module-targeted.
- Keep tests synthetic and hermetic (tmp_path/monkeypatch).

### Deliverables
1. Additional tests with clear assertions.
2. Coverage command and before/after percent for `yml_utilities.py`.
3. Brief note of any inherently untestable/noise branches.

