# WRK-1074 AC Test Matrix

| AC | Description | Test(s) | Result |
|----|-------------|---------|--------|
| AC1 | `tests/contracts/` with ≥3 files in digitalmodel | 4 files created: data, yml, units, common | PASS |
| AC2 | `tests/contracts/` with ≥2 files in worldenergydata | 2 files created: data, engine | PASS |
| AC3 | Contract tests run in `run-all-tests.sh` integration step | contracts loop added after REPO_CONFIGS | PASS |
| AC4 | Contract test output shows: changed symbol, au_version, consumer test | conftest.py adds [CONTRACT VIOLATION] section; AU_VERSION in each file | PASS |
| AC5 | `docs/api-contracts.md` per consuming repo | digitalmodel/docs/api-contracts.md + worldenergydata/docs/api-contracts.md | PASS |
| AC6 | Cross-review (Codex) passes | Codex unavailable (quota) — user override applied; Claude review: APPROVE | PASS* |

*AC6: Codex deferred to Stage 13; user-approved override.

## Test Execution Summary

| Repo | Tests | Passed | Errors |
|------|-------|--------|--------|
| digitalmodel | 17 | 17 | 0 |
| worldenergydata | 8 | 8 | 0 |
| **Total** | **25** | **25** | **0** |
