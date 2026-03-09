# AC Test Matrix — WRK-1057

| Test | Scenario | Expected | Result |
|------|----------|----------|--------|
| AC1: submodule coverage | Run scripts/repo-health.sh | >20 rows (hub + all submodules) | PASS (29 rows) |
| AC2: columns present | Header row | BRANCH, DIRTY, LAST-COMMIT, TESTS | PASS |
| AC3: --json flag | Machine-readable output | Valid JSON array with repo/branch/dirty/test_result fields | PASS (25 repos) |
| AC4: graceful absent test logs | No logs/tests/ dir | Shows "unknown", no crash | PASS |
| AC5: test log integration | logs/tests/workspace-hub-last.txt = "pass" | Row shows "pass" | PASS |
| AC6: /today section collapsible | section script | HTML details block | PASS |

All 6 ACs: PASS. 0 FAIL.
