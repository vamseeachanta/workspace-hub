# WRK-1158 Test Results

## check-gates-green.sh (8 tests)

| Test | Result |
|------|--------|
| all-OK: exits 0 | PASS |
| all-OK: summary shows 3 OK | PASS |
| MISSING-gate: exits 1 | PASS |
| MISSING-gate: lists missing gate name | PASS |
| MISSING-gate: summary shows 1 missing | PASS |
| WARN-only: exits 0 (WARN does not fail) | PASS |
| WARN-only: summary shows 0 missing | PASS |
| infra-failure: exit 2 propagated | PASS |

## print-gate-passed.sh (14 tests)

| Test | Result |
|------|--------|
| stage 7 approved exits 0 | PASS |
| stage 7 prints GATE PASSED | PASS |
| stage 7 prints checkpoint prompt | PASS |
| stage 17 approved exits 0 | PASS |
| stage 17 prints GATE PASSED | PASS |
| stage 7 pending exits 1 | PASS |
| stage 7 pending says not approved | PASS |
| missing evidence exits 1 | PASS |
| missing evidence reports error | PASS |
| invalid stage exits 1 | PASS |
| invalid stage reports error | PASS |
| no args exits 1 | PASS |
| stage 7 'approved' also exits 0 | PASS |
| stage 7 'approved' prints GATE PASSED | PASS |

**Total: 22 passed, 0 failed**
