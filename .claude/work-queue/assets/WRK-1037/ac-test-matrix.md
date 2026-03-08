# AC Test Matrix — WRK-1037

| # | Acceptance Criteria | Test | Status |
|---|---------------------|------|--------|
| T1 | run_renderer(): if uv present but broken → surfaces error, not silent fallback | test-uv-readiness.sh Scenario 2 | PASS |
| T2 | uv readiness probe added: uv present+working → exits 0 | test-uv-readiness.sh Scenario 1 | PASS |
| T3 | uv readiness probe: uv present+broken → surfaces error | test-uv-readiness.sh Scenario 2 | PASS |
| T4 | uv readiness probe: uv absent → no "not functional" error (python3 fallback) | test-uv-readiness.sh Scenario 3 | PASS |
| T5 | cross-review.sh: Codex CLI not found → explicit warning + exit 1 without --allow-no-codex | test-cross-review-codex-hardgate.sh Scenario 4 | PASS |
| T6 | cross-review.sh: Codex CLI not found + --allow-no-codex → 2-of-3 fallback allowed | test-cross-review-codex-hardgate.sh Scenario 5 | PASS |
| T7 | test-submit-to-codex-robustness.sh still passes | 31/31 | PASS |
| T8 | test-codex-fallback.sh still passes | 20/20 | PASS |
| T9 | test-cross-review-path-sanitization.sh still passes | 4/4 | PASS |
| T10 | test-cross-review-codex-hardgate.sh: CLI missing exits non-zero without flag | Scenario 4 | PASS |
