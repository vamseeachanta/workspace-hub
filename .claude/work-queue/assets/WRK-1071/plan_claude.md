---
wrk_id: WRK-1071
title: "feat(harness): performance benchmark harness — regression detection for engineering calculations"
domain: harness/performance-profiling
complexity: medium
route: B
created_at: 2026-03-10
target_repos: [assetutilities, digitalmodel, worldenergydata]
status: revised-post-cross-review
version: "1.1"
codex_verdict: MAJOR_RESOLVED
gemini_verdict: MINOR_RESOLVED
---

## Mission

Establish performance baselines for compute-heavy engineering calculations so
regressions are caught before they reach production reports.

## Phase 1 — pytest-benchmark integration (TDD first)

**Tests first** (`scripts/testing/test_run_benchmarks.py`, 8 tests):
- `test_run_benchmarks_all_repos_exit_zero` — script returns 0 on clean run
- `test_run_benchmarks_single_repo` — `--repo assetutilities` runs only that suite
- `test_save_baseline_writes_json` — `--save-baseline` writes `config/testing/benchmark-baseline.json`
- `test_regression_detection_flags_slowdown` — injected 25% slowdown → exit 1
- `test_no_regression_passes` — baseline-equal result → exit 0
- `test_missing_baseline_exits_with_bootstrap_error` — no baseline + no `--no-compare` → exit 2 with clear message
- `test_invalid_repo_name_exits_nonzero` — `--repo invalid` → exit 1, informative error
- `test_new_benchmark_not_in_baseline_warns_not_fails` — new bench entry absent from baseline → WARN, exit 0

**assetutilities** (`testpaths = ["tests"]` already in pytest.ini → root `tests/` is correct):
- Add `pytest-benchmark>=4.0.0,<5.0.0` to `[dependency-groups].test`
- Create `assetutilities/tests/benchmarks/__init__.py`
- Create `assetutilities/tests/benchmarks/test_scr_fatigue_benchmarks.py`
  - `bench_keulegan_carpenter_number(benchmark)` — synthetic (D, U, T) inputs
  - `bench_soil_interaction_fatigue_factor(benchmark)` — synthetic soil profile

Note: assetutilities CP calcs live in digitalmodel. assetutilities targets
riser/fatigue calcs (`scr_fatigue.py`) — `keulegan_carpenter_number`, `soil_interaction_fatigue_factor`.

**digitalmodel** (pytest-benchmark already installed; `tests/benchmarks/` exists with generic benchmarks):
- Audit `tests/benchmarks/` before adding — do not disturb existing generic benchmark files
- Create `digitalmodel/tests/benchmarks/test_cp_benchmarks.py` (new file only):
  - `bench_cp_abs_gn_ships(benchmark)` — ABS_gn_ships_2018 cfg dict
  - `bench_cp_dnv_rp_f103(benchmark)` — DNV_RP_F103_2010 cfg dict
  - `bench_cp_abs_gn_offshore(benchmark)` — ABS_gn_offshore_2018 cfg dict
  - `bench_cp_dnv_rp_b401(benchmark)` — DNV_RP_B401_offshore cfg dict
- Create `digitalmodel/tests/benchmarks/test_wall_thickness_benchmarks.py`:
  - `bench_wall_thickness_dnv(benchmark)` — synthetic DNV-ST-F101 input
- run-benchmarks.sh specifies these files explicitly (not whole `tests/benchmarks/`)

Import path: `from digitalmodel.infrastructure.base_solvers.hydrodynamics.cathodic_protection import CathodicProtection`
(not the deprecated `infrastructure.common` shim)

**worldenergydata** (pytest-benchmark only in optional-dev — not auto-activated by `uv run`):
- Move `pytest-benchmark>=4.0.0,<5.0.0` to new `[dependency-groups].benchmark` in pyproject.toml
- Keep benchmarks in `tests/performance/` to reuse existing `conftest.py` BenchmarkFixture:
  - Create `worldenergydata/tests/performance/test_eia_benchmarks.py`
  - `bench_state_production_loader(benchmark)` — 1000 synthetic EIA records
  - `bench_basin_production_loader(benchmark)` — 500 synthetic basin records
- run-benchmarks.sh targets `tests/performance/test_eia_benchmarks.py` explicitly

## Phase 2 — run-benchmarks.sh + baseline tooling

**`scripts/testing/run-benchmarks.sh`** (modelled on `run-all-tests.sh` from WRK-1054):
```
REPOS = [
  {name: assetutilities, dir: assetutilities, pythonpath: src, targets: tests/benchmarks},
  {name: digitalmodel, dir: digitalmodel, pythonpath: src,
   targets: "tests/benchmarks/test_cp_benchmarks.py tests/benchmarks/test_wall_thickness_benchmarks.py"},
  {name: worldenergydata, dir: worldenergydata, pythonpath: "src:../assetutilities/src",
   targets: tests/performance/test_eia_benchmarks.py},
]
```
- Per-repo: `cd <dir> && uv run python -m pytest <targets> --benchmark-only --benchmark-json=<tmp> -q`
  (cd into repo dir so uv binds to that repo's lockfile and deps)
- Collect results → `scripts/testing/benchmark-results/benchmark-YYYY-MM-DD.json`
  Baseline keys are repo-qualified: `assetutilities::bench_keulegan_carpenter_number`, etc.
- `--repo <name>` — single-repo run; compare only that repo's entries
- `--save-baseline` — writes `config/testing/benchmark-baseline.json` from latest run
- `--no-compare` — skips comparison (bootstrap / first run)
- Default compare mode:
  - Missing baseline file → exit 2 with clear bootstrap message (not silent fail)
  - New benchmark not in baseline → WARN, do not fail (exit 0)
  - Benchmark mean >20% slower → REGRESSION, exit 1

**`scripts/testing/parse_benchmark_output.py`**:
- Reads pytest-benchmark JSON; compares means against baseline
- Prints regression table; exits 1 if any regression found

`.gitignore`: add `scripts/testing/benchmark-results/` (runtime artifacts)

## Phase 3 — cron + integration

- Add weekly cron entry to `scripts/cron/crontab-template.sh` (follow existing `$WORKSPACE_HUB` pattern):
  `0 4 * * 0 PATH=$HOME/.local/bin:$PATH; cd $WORKSPACE_HUB && bash scripts/testing/run-benchmarks.sh >> $WORKSPACE_HUB/logs/quality/benchmark-cron.log 2>&1`
  (explicit PATH ensures `uv` is found in cron's restricted shell)
- Bootstrap baseline: `./scripts/testing/run-benchmarks.sh --save-baseline --no-compare`
- `config/testing/benchmark-baseline.json` committed from initial run
- `scripts/testing/benchmark-results/` added to `.gitignore`

## Test Strategy

| Layer | What | When |
|-------|------|------|
| TDD harness | 5 tests in `test_run_benchmarks.py` | Before implementation |
| Unit (benchmark) | Each `bench_*` function runs without error | Each commit |
| Integration | `run-benchmarks.sh` exits 0 | Before merge |
| Regression gate | >20% slowdown = exit 1 | Weekly cron + pre-merge |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| worldenergydata pytest-benchmark only in optional-dev deps | Medium | Medium | Verify `uv run` activates group; add to `[dependency-groups].benchmark` if needed |
| Benchmark variance causing false positives | Medium | Low | Use `--benchmark-min-rounds=5`; flag only >20% (not >5%) |
| assetutilities test path is `src/assetutilities/tests/` not root `tests/` | Low | Medium | Create `tests/benchmarks/` at repo root; update pytest config if needed |
| CP calcs location mismatch in WRK body | Confirmed | Fixed | Plan explicitly targets digitalmodel for CP; assetutilities targets scr_fatigue.py |

## Out of Scope

- Benchmark results dashboard (WRK-1057 repo-health integration — follow-on)
- assethold / ogmanufacturing benchmarks (no heavy calc modules identified)
- Historical regression tracking beyond baseline comparison
