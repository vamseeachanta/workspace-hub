# WRK-1071 Acceptance Criteria Test Matrix

| # | Acceptance Criterion | Test / Validation | Result |
|---|---------------------|-------------------|--------|
| AC-1 | Benchmark harness runs all 3 repos via single command | `bash scripts/testing/run-benchmarks.sh --save-baseline --no-compare` → all 3 repos execute, exit 0 | PASS |
| AC-2 | assetutilities SCR fatigue benchmarks collect and run | 2 tests collected and run (KC number, soil interaction sweep), results written to JSON | PASS |
| AC-3 | digitalmodel CP benchmarks — all 4 routes benchmark | 4 CP route tests (ABS ships, DNV F103, ABS offshore, DNV B401) + 1 wall-thickness = 5 pass | PASS |
| AC-4 | worldenergydata EIA benchmarks collect and run | 2 EIA loader tests (state 1000 records, basin 500 records) pass, results JSON written | PASS |
| AC-5 | Baseline save writes valid JSON with repo-qualified keys | `--save-baseline` writes 9-entry JSON; keys like `assetutilities::test_bench_keulegan_carpenter_number` | PASS |
| AC-6 | Self-comparison (same run vs baseline) exits 0 | Second run vs just-saved baseline exits 0, all deltas within ±20% | PASS |
| AC-7 | Missing baseline → exit 2 with helpful message | `test_missing_baseline_exits_with_bootstrap_error` TDD test PASS | PASS |
| AC-8 | Unknown --repo name → exit nonzero with informative error | `test_invalid_repo_name_exits_nonzero` TDD test PASS | PASS |
| AC-9 | New benchmark not in baseline warns but does not exit 1 | `test_new_benchmark_not_in_baseline_warns_not_fails` TDD test PASS (exit 0) | PASS |
| AC-10 | Cron entry added to crontab-template.sh | Nightly 01:30 entry with explicit PATH for uv added to `scripts/cron/crontab-template.sh` | PASS |
| AC-11 | uv.lock updated for both repos | `uv lock` run in assetutilities (added pytest-benchmark 4.0.0) and worldenergydata (downgraded to 4.0.0) | PASS |
| AC-12 | benchmark-results/ dir gitignored | `scripts/testing/benchmark-results/` added to `.gitignore` | PASS |
