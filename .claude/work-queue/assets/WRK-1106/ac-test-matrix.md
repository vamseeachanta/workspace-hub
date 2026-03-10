# WRK-1106 Acceptance Criteria Test Matrix

| # | Test | Command | Result |
|---|------|---------|--------|
| T6 | claim-item.sh exits 0 with resume message when working/ + activation.yaml (non-empty session_id) | bash test-claim-collision.sh | PASS |
| T7 | claim-item.sh exits 1 when working/ + activation.yaml (empty session_id) | bash test-claim-collision.sh | PASS |
| T1 | collision guard preserved — exits 1 when no activation.yaml | bash test-claim-collision.sh | PASS |
| T4 | collision guard — session-lock details shown | bash test-claim-collision.sh | PASS |
| - | All 9 tests pass | bash scripts/work-queue/tests/test-claim-collision.sh | PASS |
