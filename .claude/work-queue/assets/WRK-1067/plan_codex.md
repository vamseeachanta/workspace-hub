# Codex Review: REQUEST_CHANGES

## Verdict: REQUEST_CHANGES

### Issues Found
- Parsing pytest-cov terminal output with grep/awk is brittle; use --cov-report=json instead
- Ratchet threshold of -2% allows gradual coverage decay; suggest 0% or max(80, baseline-2)
- Dynamic detection of --cov-fail-under from pyproject.toml is fragile
- SKIP_COVERAGE=1 has no audit trail; require reason string

### Suggestions
- Use --cov-report=json and parse JSON in check_coverage_ratchet.py
- Set threshold to max(80, baseline_pct - 2) for hard floor + ratchet
- Centralize coverage config in harness rather than detecting per-repo pyproject.toml
- Log bypass reason to audit artifact
