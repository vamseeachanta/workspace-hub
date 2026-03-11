# WRK-1095 Plan Draft Review

## Summary

Convert radon's warn-only complexity check into a ratchet gate across all 5 tier-1 repos.
Modelled on the existing mypy ratchet (WRK-1092). Complexity can only decrease or hold steady.

## Route: A (Simple)

## Plan Steps

1. **`config/quality/complexity-baseline.yaml`** — write baseline from live radon data
   - assetutilities: avg=3.03, high_cc=9, very_high_cc=2
   - digitalmodel: avg=3.48, high_cc=72, very_high_cc=15 (legacy — ratchet, not absolute block)
   - worldenergydata: avg=3.55, high_cc=39, very_high_cc=3
   - assethold: avg=3.07, high_cc=1, very_high_cc=1
   - OGManufacturing: avg=1.72, high_cc=0, very_high_cc=0

2. **`scripts/quality/check_complexity_ratchet.py`** — ratchet script
   - `--init`: capture baseline from radon
   - Ratchet: FAIL if high_cc_count or very_high_cc_count increases above baseline
   - Auto-update on improvement (no auto-commit)
   - `SKIP_COMPLEXITY_REASON` env bypass (audited)
   - Exit 0=PASS, 1=FAIL

3. **TDD tests** — `scripts/quality/tests/test_check_complexity_ratchet.py`
   - test_load_baseline, test_ratchet_pass, test_ratchet_fail_high_cc,
     test_ratchet_fail_very_high_cc, test_auto_update_baseline

4. **`check-all.sh --complexity-ratchet` flag** — upgrade radon from warn to gate

5. **`scripts/hooks/pre-push.sh`** — add complexity ratchet call

## Key Design Decision

CC>20 is tracked as a ratchet (baseline-relative), not an absolute hard block.
Reason: digitalmodel already has 15 CC>20 functions (legacy). Absolute block would
immediately fail every push. Ratchet enforces: no NEW CC>20 functions can be added.

## Files Changed

- `config/quality/complexity-baseline.yaml` (new)
- `scripts/quality/check_complexity_ratchet.py` (new, ~200 lines)
- `scripts/quality/tests/test_check_complexity_ratchet.py` (new, ~150 lines)
- `scripts/quality/check-all.sh` (extend flag)
- `scripts/hooks/pre-push.sh` (extend gate)

## Test Strategy

- Unit tests via pytest (5 tests)
- Manual: `uv run --no-project python scripts/quality/check_complexity_ratchet.py --init`
- Integration: `bash scripts/quality/check-all.sh --complexity-ratchet`
