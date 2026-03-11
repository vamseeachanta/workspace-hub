# WRK-1067 Plan: Test Coverage Enforcement

## Mission
Make the 80% coverage minimum verifiable and enforced at push time.

## Implementation Steps

### Step 1 — TDD: Write tests first
File: `scripts/testing/tests/test_coverage_gate.py`
- Test `--coverage` flag is accepted by `run-all-tests.sh` (argparse/getopt)
- Test `coverage-baseline.yaml` schema validation (required fields: repo, coverage_pct, reason if exempt)
- Test ratchet logic: `check_coverage_ratchet.py` — PASS when actual >= baseline-2, FAIL otherwise
- Test exemption override: repo with `exempt: true` skips ratchet check
- Test report file written to `scripts/testing/coverage-reports/`

### Step 2 — `run-all-tests.sh` extension
Add `--coverage` flag to argument parser:
- When set: append `--cov=<src> --cov-report=term-missing --cov-fail-under=80` to pytest invocation per repo
- But: skip `--cov-fail-under=80` for repos that already declare it in `pyproject.toml` addopts (assethold)
- After each repo run, extract TOTAL coverage % from output: `grep '^TOTAL' | awk '{print $NF}'`
- Write per-repo result to `scripts/testing/coverage-reports/WRK-NNN-coverage-YYYYMMDD.txt`

### Step 3 — `scripts/testing/check_coverage_ratchet.py`
New script:
```
usage: check_coverage_ratchet.py --baseline config/testing/coverage-baseline.yaml
                                  --results  coverage-results.json
```
- Reads baseline YAML; reads JSON results (repo → pct)
- For each repo: skip if `exempt: true`; FAIL if actual < baseline_pct - 2
- Exit 0 = all pass; Exit 1 = ratchet breached (prints which repos failed)

### Step 4 — `config/testing/coverage-baseline.yaml`
Run `run-all-tests.sh --coverage` once to capture real numbers. Structure:
```yaml
repos:
  assetutilities:
    coverage_pct: <captured>
    updated_at: "2026-03-09"
  assethold:
    coverage_pct: <captured>
    updated_at: "2026-03-09"
  digitalmodel:
    coverage_pct: <captured>
    updated_at: "2026-03-09"
  worldenergydata:
    coverage_pct: <captured>
    updated_at: "2026-03-09"
```
Exemption example:
```yaml
  some_repo:
    coverage_pct: 45
    exempt: true
    exempt_reason: "legacy untested module — WRK-XXXX tracks remediation"
```

### Step 5 — `scripts/hooks/pre-push.sh` extension
Add coverage gate after gitleaks check:
```bash
if [[ "${SKIP_COVERAGE:-0}" != "1" ]]; then
    bash "${REPO_ROOT}/scripts/testing/run-all-tests.sh" --coverage
    uv run --no-project python "${REPO_ROOT}/scripts/testing/check_coverage_ratchet.py" \
        --baseline "${REPO_ROOT}/config/testing/coverage-baseline.yaml"
fi
```
`SKIP_COVERAGE=1 git push` available for emergency bypass.

## Test Strategy
- Unit tests for ratchet logic using fixture YAML/JSON inputs (no live pytest runs)
- Integration: run `run-all-tests.sh --coverage --repo assethold` in CI to verify report generation
- Baseline capture: one-time manual run to populate YAML before hook activates

## Files Created/Modified
| File | Action |
|------|--------|
| `scripts/testing/run-all-tests.sh` | modify — add `--coverage` flag |
| `scripts/testing/check_coverage_ratchet.py` | create |
| `scripts/testing/tests/test_coverage_gate.py` | create |
| `config/testing/coverage-baseline.yaml` | create |
| `scripts/testing/coverage-reports/.gitkeep` | create |
| `scripts/hooks/pre-push.sh` | modify — add coverage gate |

## Risks & Mitigations
- Coverage runs slow: opt-in via `--coverage` flag (not default); `SKIP_COVERAGE=1` bypass
- assethold double-adds `--cov-fail-under`: detect via `pyproject.toml` grep and skip
- digitalmodel/worldenergydata PYTHONPATH: pass through existing env var handling in run_repo()
