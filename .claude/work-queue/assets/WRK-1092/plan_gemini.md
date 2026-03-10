# WRK-1092 Plan — Gemini Review Input

## Objective
Add a mypy error count ratchet to prevent type-safety regression across 5 repos.

## Approach
Model after existing `scripts/testing/check_coverage_ratchet.py`:
- YAML baseline file at `config/quality/mypy-baseline.yaml`
- New script `scripts/quality/check_mypy_ratchet.py`
- Runs mypy inline, parses stdout, compares to baseline
- Auto-updates baseline on improvement (ratchet moves forward only)

## Integration
- `check-all.sh --mypy-ratchet`: delegates to script
- `pre-push.sh`: adds mypy ratchet check after coverage gate

## Test plan
≥5 unit tests with mocked subprocess, fixture YAML baselines.
TDD: tests first, then implementation.
