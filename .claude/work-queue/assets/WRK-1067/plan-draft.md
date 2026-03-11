# WRK-1067 Plan: Test Coverage Enforcement (Revised after cross-review)

## Mission
Make the 80% coverage minimum verifiable and enforced at push time.

## Changes from Draft (addressing cross-review)
- Use `--cov-report=json` (structured) instead of terminal `grep/awk`
- Enforce `actual >= max(80, baseline_pct - 2)` — hard floor + ratchet
- Do NOT pass `--cov=src` from harness; rely on each repo's `[tool.coverage.run]` source
- Bypass requires `SKIP_COVERAGE_REASON=...` env var; logged to coverage report artifact
- Remove dynamic `pyproject.toml` detection of `--cov-fail-under`; harness owns enforcement

## Implementation Steps

### Step 1 — TDD: Write tests first
File: `scripts/testing/tests/test_coverage_gate.py`
- Test ratchet logic: `actual >= max(80, baseline - 2)` → PASS; below → FAIL
- Test exemption: `exempt: true` in baseline → skip gate
- Test bypass logging: `SKIP_COVERAGE_REASON` present → writes skip record to report
- Test JSON parsing: given `coverage.json` with TOTAL %, extract correctly
- Test report file creation: verify `coverage-reports/` file written with correct content

### Step 2 — `scripts/testing/check_coverage_ratchet.py` (new script)
```
usage: check_coverage_ratchet.py
    --baseline config/testing/coverage-baseline.yaml
    --results-dir <repo_root>  # reads coverage.json from each repo root
    [--report-out scripts/testing/coverage-reports/WRK-NNN-coverage-YYYYMMDD.txt]
```
Logic per repo:
1. Skip if `exempt: true` in baseline
2. Read `{repo_root}/coverage.json` → extract `totals.percent_covered_display`
3. Pass if `actual >= max(80.0, baseline_pct - 2.0)`
4. Fail with clear message: `{repo}: {actual:.1f}% < floor {floor:.1f}% (baseline={baseline:.1f}%)`
5. Write summary report to `--report-out` (includes bypass record if SKIP_COVERAGE_REASON set)
Exit 0 = all pass; Exit 1 = any repo breached

### Step 3 — `scripts/testing/run-all-tests.sh` extension
Add `--coverage` flag:
- When set: append `--cov-report=json --cov-report=term-missing` to pytest args per repo
- Do NOT append `--cov=<src>` (repos own their source config)
- Do NOT append `--cov-fail-under=80` (ratchet script handles gate; let repo pyproject.toml addopts stand)
- After all repos complete, pass `--results-dir` entries to ratchet script
- Coverage reports written to `scripts/testing/coverage-reports/`

### Step 4 — `config/testing/coverage-baseline.yaml` (new file)
Populated by running `run-all-tests.sh --coverage` once. Schema:
```yaml
schema_version: "1"
updated_at: "YYYY-MM-DD"
repos:
  assetutilities:
    coverage_pct: <float>
    updated_at: "YYYY-MM-DD"
  assethold:
    coverage_pct: <float>
    updated_at: "YYYY-MM-DD"
  digitalmodel:
    coverage_pct: <float>
    updated_at: "YYYY-MM-DD"
  worldenergydata:
    coverage_pct: <float>
    updated_at: "YYYY-MM-DD"
# Exemption example:
#   legacy_module:
#     coverage_pct: 45
#     exempt: true
#     exempt_reason: "legacy untested — WRK-XXXX tracks remediation"
#     updated_at: "YYYY-MM-DD"
```

### Step 5 — `scripts/hooks/pre-push.sh` extension
```bash
if [[ -z "${SKIP_COVERAGE_REASON:-}" ]]; then
    bash "${REPO_ROOT}/scripts/testing/run-all-tests.sh" --coverage
else
    echo "[pre-push] Coverage gate skipped. Reason: ${SKIP_COVERAGE_REASON}" >&2
fi
```
Bypass: `SKIP_COVERAGE_REASON="hotfix: deploy blocker" git push`
Reason is logged in the coverage report artifact (even when skipping).

## Files Created/Modified
| File | Action |
|------|--------|
| `scripts/testing/run-all-tests.sh` | modify — add `--coverage` flag |
| `scripts/testing/check_coverage_ratchet.py` | create |
| `scripts/testing/tests/test_coverage_gate.py` | create |
| `config/testing/coverage-baseline.yaml` | create |
| `scripts/testing/coverage-reports/.gitkeep` | create |
| `scripts/hooks/pre-push.sh` | modify — add coverage gate |

## Test Strategy
- Unit tests for ratchet logic using fixture YAML/JSON inputs (no live pytest runs needed)
- Fixture JSON files mimic `coverage.json` `totals.percent_covered_display` field
- Integration smoke: `run-all-tests.sh --coverage --repo assethold` verifies report file written

## Risks & Mitigations
| Risk | Mitigation |
|------|-----------|
| Coverage runs slow at push time | Opt-in `--coverage` flag; bypass with `SKIP_COVERAGE_REASON` |
| assethold `--cov-fail-under=80` in addopts causes double-fail | Not a problem — ratchet gate is separate; pytest exits 1 but we parse JSON, not exit code |
| coverage.json location varies | Standardize: write to repo root; harness reads `{repo_root}/coverage.json` |
| digitalmodel/worldenergydata PYTHONPATH | Existing `run_repo()` PYTHONPATH handling unchanged |
