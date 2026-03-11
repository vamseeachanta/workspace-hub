# Codex Cross-Review: WRK-1067 Plan

## Verdict: REQUEST_CHANGES (resolved in revised plan)

### Summary
Architecture is sound but brittle terminal parsing and permissive ratchet threshold require revision.

### Issues Found
- Parsing pytest-cov terminal output with grep/awk is brittle
- Ratchet threshold -2% too permissive; allows gradual decay
- Dynamic pyproject.toml detection for --cov-fail-under is fragile
- SKIP_COVERAGE=1 has no audit trail

### Resolution in revised plan
- Use --cov-report=json; parse coverage.json in check_coverage_ratchet.py
- Enforce actual >= max(80, baseline_pct - 2) — hard floor + ratchet
- Remove dynamic pyproject.toml detection; harness owns enforcement
- Changed to SKIP_COVERAGE_REASON=... with logging to report artifact
