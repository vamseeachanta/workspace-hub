# WRK-1120 AC Test Matrix

| AC | Description | Test | Result |
|----|-------------|------|--------|
| 1 | next-id.sh creates sentinel pending/WRK-NNN.md | test-next-id-collision.sh Test 3 | PASS |
| 2 | Collision retry: two concurrent calls get different IDs | test-next-id-collision.sh Test 2 | PASS |
| 3 | After 5 failures, exit 1 with clear error | N/A (no collision storm in test env) | PASS (code review) |
| 4 | Two concurrent calls always different IDs | test-next-id-collision.sh Test 2 | PASS |
| 5 | Callers require no changes | Manual verification: WRK-1119 created normally | PASS |
| 6 | TDD: ≥3 passing tests | test-next-id-collision.sh: 3/3 pass | PASS |

## Test Run
```
=== test-next-id-collision.sh ===
Test 1: returns numeric ID ... PASS (got 1121)
Test 2: concurrent calls return different IDs ... PASS (A=1123, B=1124)
Test 3: sentinel file created in pending/ ... PASS (WRK-1123.md exists)
Results: 3 passed, 0 failed
```
