# Plan for #3787: stop paying the pytest startup tax on lanes that cannot use it

**Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3787
**Status:** **plan-approved** (owner, 2026-08-03; marker `.planning/plan-approved/3787.md`)
**Lane:** `lane:claude` · **Complexity:** T2 · **Client:** N/A
**Review:** r1 Codex **MAJOR** + Claude **MAJOR**; r2 applied inline.
Artifacts: `scripts/review/results/2026-08-03-plan-3787-{claude,codex,disagreement}.md`

> **Restored 2026-08-03 after loss.** Originally written untracked and removed by the
> auto-sync clean. Committed this time — see #3791.

## Resource Intelligence Summary

| Path | Role |
|---|---|
| `worldenergydata/tests/conftest.py:256-262` | constructs the tracker at `pytest_configure`; DB path hardcoded at :261 |
| `worldenergydata/src/.../performance/database.py:44-60` | `__init__` calls `_init_database()` — construction *is* DB access |
| `worldenergydata/tests/conftest.py:302` | `detect_regressions(lookback_days=7)`, unconditional |
| `digitalmodel/pytest.ini:34-39` | global `addopts`; `pyproject.toml:263-268` confirms it wins outright |
| `pytest_benchmark/utils.py:149` | `subprocess_output` — git metadata at plugin init |

**Reproduction, measured on this box**

```
git describe --dirty --always --long   (digitalmodel)  = 38,158 ms
worldenergydata/.test_performance.db                   = 59 MB, 105,348 execution rows

pytest --collect-only:  assetutilities  7.56s (1,352 tests)
                        worldenergydata >180s
                        digitalmodel    >180s
trivial single file:    digitalmodel 1.50s · assetutilities 4.38s
```

**Gap:** the two slow repos are unclassified beyond 180s — forward progress demonstrated,
completion within 900s not proven. Their "before" figures are **censored values, not
durations**, and must not be reported as measurements.

## Governing constraint

**Remove the tax from the fast path. Do not remove the capability.**
`pytest-randomly` surfaces order-dependent tests and digitalmodel **has them**
(cathodic-protection and `workflow_api` pass alone, fail in-suite). Benchmark git metadata
is waste on collect-only and legitimate on a benchmark run. The regression analysis is
legitimate after a real session. The nightly/full sweep keeps all of it.

Anything reducing coverage to buy speed is out of scope and must be reported, not done.

## Deliverable

`--collect-only` completes well inside the 30s pre-push budget in both repos, with
**identical collected-test counts** on the full lane.

## Files to Change

| File | Change |
|---|---|
| `worldenergydata/tests/conftest.py` | lazy tracker (`pytest_configure`, not just session finish); **add a DB-path seam** |
| `worldenergydata/src/.../performance/database.py` | possibly, if laziness is cleaner at construction |
| `digitalmodel/` **fast-lane invocation only** | `-p no:...`. **NOT `pytest.ini`** — its `addopts` is global and would disable plugins for the nightly sweep too |

## Pseudocode

```python
def pytest_configure(config):
    _performance_tracker = LazyTracker(db_path_provider)   # construct nothing yet

# session finish
if not _performance_tracker.was_used():
    return      # nothing executed; nothing to analyse
```

Laziness subsumes `collectonly` rather than special-casing it, and also covers a session
where every test is deselected — settling OQ1 with no second predicate to remember.

## TDD Test List

1. `test_collect_only_does_not_touch_the_performance_db` — asserts the property (no DB
   access), not a wall-clock number, so a faster machine cannot satisfy it.
2. `test_real_session_still_runs_regression_analysis` — **guard against "fixing" the tax
   by deleting the feature.**
3. `test_full_lane_still_loads_every_disabled_plugin` — randomly, benchmark, faker. Widened
   from randomly-only per r1 finding 6.
4. `test_collected_count_unchanged` — necessary and **NOT sufficient**: a plugin that stops
   loading does not change the count, so this is blind to the r1 finding-5 leak. Test 3 closes it.
5. `test_db_path_is_injectable` — the seam exists and is honoured; without it test 1 is unwritable.

## Acceptance Criteria

1. Tests 1–5 pass; 1 demonstrated failing beforehand.
2. **Measured** before/after `--collect-only` wall-clock per repo on an idle box, with
   `timeout 900` so "before" is a duration and not a censored `>180s`.
3. Full-lane collected count **identical**, stated as a number both sides.
4. Each disabled plugin named with the lane where it still runs.
5. `check-no-abs-paths.sh` adds no new violations (baseline mode; bare run is rc 1 / 459 pre-existing).

## Risks

- **R1** The fastest route to a green number is a coverage regression. AC3 + test 3 close it.
- **R2** Timing on a loaded box is worthless — already invalidated one round. Measure serially.
  Note the threshold must gate *pre-existing* load; the measurement itself raises load.
- **Out of scope:** the 487 suppressed files — #3790.
