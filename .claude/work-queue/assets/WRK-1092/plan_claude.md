# WRK-1092 Plan — Claude Review

## Summary
Mypy error count ratchet: enforce monotonic type-safety improvement across 5 tier-1 repos.

## Deliverables
1. `config/quality/mypy-baseline.yaml` — per-repo error counts
2. `scripts/quality/check_mypy_ratchet.py` — ratchet logic (fail if increased, auto-update if decreased)
3. `check-all.sh --mypy-ratchet` flag
4. `scripts/hooks/pre-push.sh` — mypy ratchet gate added
5. `tests/quality/test_check_mypy_ratchet.py` — ≥5 TDD tests

## Pattern
Mirrors `check_coverage_ratchet.py` exactly. Parse mypy output inline (no separate results JSON).
Error count from "Found N errors" / 0 from "Success: no issues found".

## Risk
- mypy not installed → SKIP (exempt pattern)
- `SKIP_MYPY_REASON` env bypass for audit
