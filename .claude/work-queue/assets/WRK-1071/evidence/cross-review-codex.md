## Review Notes

**Verdict: MAJOR**

Major issues in the current draft:

- `worldenergydata` dependency activation is underspecified. `pytest-benchmark` exists only under optional `dev`, not the active dependency groups in [worldenergydata/pyproject.toml](/mnt/local-analysis/workspace-hub/worldenergydata/pyproject.toml), so `uv run` may not have the plugin at all.
- The plan puts new `worldenergydata` benchmarks under `tests/benchmarks/`, but the reusable benchmark fixtures live in [worldenergydata/tests/performance/conftest.py](/mnt/local-analysis/workspace-hub/worldenergydata/tests/performance/conftest.py). That `conftest.py` will not automatically cover a sibling tree.
- The cron command uses `<REPO_ROOT>`, but the actual template convention in [scripts/cron/crontab-template.sh](/mnt/local-analysis/workspace-hub/scripts/cron/crontab-template.sh) uses `cd $WORKSPACE_HUB && ...`. Literal placeholder expansion in crontab is a real failure mode.
- The 5 TDD tests miss the highest-risk behaviors: no-baseline bootstrap, partial/new benchmark entries, invalid repo selection, and dependency/setup failure classification.
- `digitalmodel/tests/benchmarks/` already exists and is non-empty. Running the whole directory can pull in unrelated benchmark tests and variance; the plan needs explicit scoping or an audit of the existing suite. See [digitalmodel/tests/benchmarks/conftest.py](/mnt/local-analysis/workspace-hub/digitalmodel/tests/benchmarks/conftest.py).

Minor notes:

- `assetutilities` has both root `tests/` and `src/assetutilities/tests/`; the draft should explicitly standardize on root `tests/benchmarks/` to avoid collection ambiguity. See [assetutilities/pytest.ini](/mnt/local-analysis/workspace-hub/assetutilities/pytest.ini).
- The baseline schema should use repo-qualified keys to avoid collisions across repos with similarly named benchmarks.
- `run-benchmarks.sh` should prefer `uv run --project ...` over hand-managed path assumptions, with `PYTHONPATH` used only where unavoidable.

Residual integration risk after refinement:
- Benchmark variance across machines and dependency updates can still cause noise; keeping this on one workstation and using a 20% threshold is reasonable, but the runner should label unbaselined/new tests separately from regressions.
tokens used
163,501
## Refined Plan

```yaml
---
wrk_id: WRK-1071
title: "feat(harness): performance benchmark harness — regression detection for engineering calculations"
domain: harness/performance-profiling
complexity: medium
route: B
created_at: 2026-03-10
target_repos: [assetutilities, digitalmodel, worldenergydata]
status: draft
version: "1.1"
---
```

### Mission
Establish stable, runnable performance baselines for compute-heavy engineering calculations and fail fast on meaningful regressions without introducing repo-specific env drift.

### Phase 1 — Harness contract and TDD first

**Primary harness tests** in `scripts/testing/test_run_benchmarks.py`:

1. `test_run_benchmarks_all_repos_exit_zero`
   Verifies clean run across all configured repos.

2. `test_run_benchmarks_single_repo`
   Verifies `--repo <name>` runs only the selected repo and compares only that repo’s baseline entries.

3. `test_save_baseline_writes_json`
   Verifies `--save-baseline` writes `config/testing/benchmark-baseline.json` with repo-qualified benchmark keys.

4. `test_regression_detection_flags_slowdown`
   Verifies injected 25% slowdown returns exit 1 and prints offending benchmark IDs.

5. `test_no_regression_passes`
   Verifies baseline-equal or faster results return exit 0.

**Add 4 missing edge-case tests** because the current 5 do not cover the main failure modes:

6. `test_compare_without_baseline_fails_with_actionable_message`
   If baseline file is absent and `--no-compare`/`--save-baseline` is not used, exit non-zero with bootstrap instructions.

7. `test_missing_repo_baseline_entries_warn_and_skip_new_benchmarks`
   New benchmark names should not hard-fail compare mode on first introduction; warn as “unbaselined”.

8. `test_worldenergydata_benchmark_dependency_missing_fails_cleanly`
   Verifies missing `pytest-benchmark` in `worldenergydata` produces a deterministic setup error, not a misleading regression result.

9. `test_invalid_repo_name_exits_nonzero`
   Prevent silent no-op when `--repo` is misspelled.

### Phase 2 — Repo benchmark integration

**assetutilities**
- Add `pytest-benchmark>=4.0.0,<5.0.0` to `[dependency-groups].test`.
- Keep benchmark files under root `tests/benchmarks/`, not `src/assetutilities/tests/`, because repo discovery already points at root `tests` and the repo has split test trees.
- Create `tests/benchmarks/test_scr_fatigue_benchmarks.py`:
