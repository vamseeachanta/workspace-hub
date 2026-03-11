# WRK-1081 Test Results

## TDD Status: GREEN

### test_check_all_static.sh — 23/23 passed

| Test | Description | Result |
|------|-------------|--------|
| T1 | --help shows --static/--bandit/--radon/--vulture (4 asserts) | PASS |
| T2 | bandit MEDIUM finding blocks (exit 1 + FAIL in output) | PASS |
| T3 | bandit LOW-only warns (exit 0 + WARN line visible) | PASS |
| T4 | bandit baseline suppresses existing MEDIUM → exit 0 | PASS |
| T5 | LOW-only bandit scan exits 0 (Pass 2 with -ll) | PASS |
| T6 | LOW findings visible via non-blocking Pass 1 | PASS |
| T7 | radon C-grade is non-blocking (exit 0 + radon: in output) | PASS |
| T8 | vulture dead code is non-blocking (exit 0 + WARN in output) | PASS |
| T9 | --static runs bandit + radon + vulture (3 asserts) | PASS |
| T10 | Pass 1 scan failure prints visible WARN, exits 0 | PASS |
| T11 | pre-commit MEDIUM blocks (exit 1) | PASS |
| T12 | pre-commit existing baselined MEDIUM passes (exit 0) | PASS |

### test_check_all.sh — 35/35 passed (no regressions)

Run: `bash tests/quality/test_check_all.sh`

## Acceptance Criteria Coverage

- [x] check-all.sh runs bandit, radon, vulture per repo (T9)
- [x] bandit: MEDIUM+ blocks; LOW warns (T2, T3, T6)
- [x] radon: complexity C+ reported; non-blocking (T7)
- [x] vulture: 80%+ confidence dead code reported as warning (T8)
- [x] .bandit allowlist per repo: [tool.bandit] in pyproject.toml
- [x] bandit-baseline-{repo}.json captures existing violations
- [x] bandit added to pre-commit hooks (staged files, -ll)
