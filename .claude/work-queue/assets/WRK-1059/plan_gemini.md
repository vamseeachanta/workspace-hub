# WRK-1059 Plan (Route B — Claude)

## Approach
AST-based scanner for public API docstring coverage + docs/ structure validation
appended to check-all.sh as `--api` and extended `--docs` flags.

## Files Changed
- `scripts/quality/api-audit.py` (new, ~77 lines): stdlib-only AST scanner
- `scripts/quality/check-all.sh`: +3 functions + `--api` flag (~100 lines)
- `tests/quality/test_check_all.sh`: T15–T20 (35 tests total)

## Key Decisions
- Warn-only for API coverage (baseline capture, no exit 1)
- Warn-only for docs-index/changelog missing (no hard gate at this stage)
- build system detection is informational only
- Uses `uv run --no-project python` per hub script convention
