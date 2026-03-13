---
wrk_id: WRK-1160
test_file: scripts/work-queue/tests/test_retry_diagnostics.py
---

| AC | Test | Result |
|----|------|--------|
| AC1: specific gates per attempt | test_run_checks_with_retry_shows_unmet_gates_per_attempt | PASS |
| AC2: retry cap + backoff | test_run_checks_with_retry_caps_at_max, test_run_checks_with_retry_backoff_schedule | PASS |
| AC3: clear error after max | test_run_checks_with_retry_outputs_attempt_count_on_failure | PASS |
| AC4: log signal attempt count | test_run_checks_with_retry_outputs_attempt_count_on_failure | PASS |
| AC5: delta between attempts | test_run_checks_with_retry_shows_delta_between_attempts | PASS |

Existing regression: 25 tests in test_gate_verifier_hardening.py — all PASS.
