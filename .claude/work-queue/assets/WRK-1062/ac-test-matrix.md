# WRK-1062 AC Test Matrix

| AC | Test | Command | Result | Notes |
|----|------|---------|--------|-------|
| AC1 | `live_data` marker registered in assethold | `pytest --collect-only -m live_data -q --noconftest` | PASS | Marker defined in `assethold/pytest.ini` |
| AC1 | `live_data` marker registered in assetutilities | `grep live_data assetutilities/pytest.ini` | PASS | Marker defined in `assetutilities/pytest.ini` |
| AC2 | 12 assethold tests tagged live_data | `pytest --collect-only -m live_data -q --noconftest` | PASS | 12 `test_run_process` tests collected across bonds/equity/etf/portfolio/data modules |
| AC2 | 5 smoke tests tagged live_data | `pytest --collect-only -m live_data -q --noconftest` | PASS | 5 smoke tests: `test_csv_file_operations`, `test_excel_file_operations`, `test_mock_api_request`, `test_mock_financial_data_fetch`, `test_testing_environment_setup` |
| AC2 | Total live_data count = 17 | `17/1007 tests collected (990 deselected)` | PASS | 12 + 5 = 17 total live_data tests |
| AC3 | Fixture files in `tests/fixtures/data/` | `ls assethold/tests/fixtures/data/` | PASS | `ohlcv_sample.json`, `sec_filing_sample.json`, `ticker_info_sample.json` present |
| AC3 | `tests/fixtures/builders.py` exists | `ls assethold/tests/fixtures/builders.py` | PASS | File present |
| AC4 | `--include-live` flag in `run-all-tests.sh` | `grep include-live scripts/testing/run-all-tests.sh` | PASS | Lines 33/39/45/46/48/88 implement `INCLUDE_LIVE` flag and `LIVE_FLAG` variable |
| AC5 | Default run: zero unexpected failures | `pytest tests/ --noconftest -m "not live_data" -q` | PASS | `990 passed, 17 deselected, 2 warnings` — 0 failures |
| AC5 | `run-all-tests.sh --repo assethold` default run | `bash scripts/testing/run-all-tests.sh --repo assethold` | PASS | `assethold 990 0 0 0 0 ok` |
| AC6 | `refresh-fixtures.sh --dry-run` passes | `bash scripts/testing/refresh-fixtures.sh --dry-run` | PASS | `PASS: all fixture files are valid JSON (3 files checked)` |
| Baseline | assetutilities 0 live_data failures | `pytest tests/ --noconftest -m "not live_data" -q` | PASS | `692 passed, 9 skipped` — 0 live_data failures |

## Summary

- **PASS count**: 12
- **FAIL count**: 0
- **Stage 12 gate**: MET (≥3 PASS, 0 FAIL)

## Run Date

2026-03-09
