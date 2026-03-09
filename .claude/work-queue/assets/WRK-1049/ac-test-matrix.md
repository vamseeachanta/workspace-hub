# WRK-1049 AC Test Matrix

| AC | Description | Test | Result |
|----|-------------|------|--------|
| AC1 | process.md Step 4 is script-first redirect (no bash mv) | Manual inspection of process.md | PASS |
| AC2 | claim-item.sh exits 1 when WRK already in working/ | T1 test-claim-collision.sh | PASS |
| AC3 | session-lock.yaml written at Stage 1 with pid/hostname/locked_at | T2, T3 test-claim-collision.sh | PASS |
| AC4 | collision error message includes session-lock details | T4 test-claim-collision.sh | PASS |
| AC5 | All 6 tests pass | bash scripts/work-queue/tests/test-claim-collision.sh | PASS |
