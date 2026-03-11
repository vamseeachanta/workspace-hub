# WRK-1095 AC Test Matrix

| AC | Description | Test | Result |
|----|-------------|------|--------|
| AC1 | `config/quality/complexity-baseline.yaml` exists with per-repo stats | File exists with all 5 repos | PASS |
| AC2 | `check_complexity_ratchet.py` — ratchet logic | test_ratchet_pass, test_ratchet_fail_high_cc, test_ratchet_fail_very_high_cc | PASS |
| AC3 | Pre-push hook extended with COMPLEXITY_RATCHET_GATE=1 guard | Code review of pre-push.sh lines 214-230 | PASS |
| AC4 | `check-all.sh --complexity-ratchet` flag | `bash check-all.sh --complexity-ratchet` exits 0 | PASS |
| AC5 | ≥5 TDD tests | 6 tests in test_check_complexity_ratchet.py — all PASS | PASS |
| AC6 | Passes `check-all.sh` for script itself | `uvx ruff check` — All checks passed | PASS |

## Test Run Summary

```
6 passed in 1.78s
All checks passed! (ruff)
5 PASS, 0 FAIL (live ratchet)
```

## All ACs: PASS
