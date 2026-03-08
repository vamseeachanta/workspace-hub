# WRK-1034 Test Results

## Gate Evidence Tests

**Command**: `uv run --no-project python -m pytest tests/unit/test_verify_gate_evidence.py -q`
**Result**: 55 passed in 0.59s (2 new tests T18/T19 added in Stage 13 cross-review fix)

## Stage 7 / Stage 17 Specific Tests

**Command**: `uv run --no-project python -m pytest tests/unit/test_verify_gate_evidence.py -k "stage7 or stage17" -v`
**Result**: 19 passed in 0.29s

### Test Summary

| Test | Result |
|------|--------|
| T1: Stage 7 disabled bypass | PASS |
| T2: Stage 7 missing artifact fails | PASS |
| T3: Stage 7 all fields valid passes | PASS |
| T4: Stage 7 wrong decision fails | PASS |
| T5: Stage 7 agent confirmed_by rejected | PASS |
| T6: Stage 7 confirmed_by missing fails | PASS |
| T7: Stage 7 missing config → infra failure | PASS |
| T8: Stage 7 migration exemption passes | PASS |
| T9: Stage 17 disabled bypass | PASS |
| T10: Stage 17 missing artifact fails | PASS |
| T11: Stage 17 all fields valid passes | PASS |
| T12: Stage 17 wrong decision fails | PASS |
| T13: Stage 17 agent reviewer rejected | PASS |
| T14: Stage 7 CLI exit 0 on pass | PASS |
| T15: Stage 7 CLI exit 1 on predicate fail | PASS |
| T16: Stage 17 CLI exit 0 on pass | PASS |
| T17: Stage 17 reviewed_at union check | PASS |

## CLI Smoke Tests

| Command | Result |
|---------|--------|
| `--stage7-check WRK-1034` | PASS (exit 0) |
| `--stage5-check WRK-1034` | PASS (exit 0) |
