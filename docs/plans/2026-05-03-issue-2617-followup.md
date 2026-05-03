# Issue #2617 — Plan: Mitigate flaky `test_packaged_yaml_in_built_distribution_preserves_existing_package_data`

**Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2617
**Repo:** `digitalmodel/`
**Status:** plan-draft (Team F of 7)
**Tense:** future — no work has shipped.

## TL;DR

Three sibling tests (rudder/yaw/turning-circle) all shell out to `python -m build --wheel --no-isolation` from the **same `cwd=repo_root`**. Setuptools writes intermediate artifacts to `<repo_root>/build/` regardless of `--outdir <tmp_path>` (only the final wheel honors `--outdir`). When run on the same host concurrently — within one `pytest -n auto` (Makefile default) OR across two pytest sessions on the same checkout (e.g., `/whats-next` parallel verification) — workers race on `<repo_root>/build/` and one cleans up files another is mid-write on, producing `[Errno 2] No such file or directory` from the `build_wheel` backend.

The issue body lists 4 fix options. **Recommended: a hybrid of (a) + (d): add `xdist_group` for in-session serialization AND copy the package source tree to a per-test scratch dir so the `cwd` is unique.** The issue's "isolation" phrasing conflates two layers — see Resource Intel.

## Resource intel

### What's actually shared

| Layer | Per-test? | Notes |
|---|---|---|
| `--outdir <tmp_path>` (final wheel) | YES — pytest `tmp_path` is per-test (`pytest --basetemp` parent, per-nodeid leaf) | Not the source of the race. |
| `<repo_root>/build/` (setuptools intermediate) | **NO** — hardcoded relative to `cwd=repo_root` | **THIS is the race target.** |
| `<repo_root>/dist/` (build's default outdir) | Bypassed by `--outdir` | Not in play. |
| `*.egg-info/` at repo root | NO — shared | Secondary race target. |
| PEP 517 build env (`--no-isolation`) | NO — shares the active uv venv | Reuse is fine; not the race. |

Verified via `ls /mnt/local-analysis/workspace-hub/digitalmodel/build /mnt/local-analysis/workspace-hub/digitalmodel/dist` — both directories are present and gitignored, used by every prior wheel build.

### Three sibling tests trigger the same race

- `tests/naval_architecture/test_rudder_stock_torque_sweep.py::test_packaged_yaml_in_built_distribution_preserves_existing_package_data` (line 180)
- `tests/naval_architecture/test_yaw_moment_sweep.py::test_packaged_yaml_in_built_distribution` (line 135)
- `tests/naval_architecture/test_turning_circle_estimator.py::test_packaged_yaml_in_built_distribution` (line 112)

All use `cwd=repo_root` + `--no-isolation` + `--outdir str(tmp_path)`. The issue body names only `test_yaw_moment_sweep.py` as the proven sibling collider, but `test_turning_circle_estimator.py` is a third instance that the issue narrative misses. **Any chosen fix must apply to all three** or the flake just relocates.

### Existing infrastructure

- `pytest-xdist>=3.5.0` is already a `dependencies` entry (`digitalmodel/pyproject.toml:92`). `xdist_group` marker support ships with xdist — no new dependency.
- `Makefile:23` runs `pytest -n auto --dist loadscope`. With `loadscope`, tests in the same MODULE go to the same worker — but the three colliding tests are in three different modules, so they land on three different workers under `-n auto`. That is the in-session race vector.
- No `pytest-rerunfailures` / `pytest-flaky` installed (verified via grep).
- A `flaky` marker is registered in both `pytest.ini:23` and `pyproject.toml:[tool.pytest.ini_options]:253`, but the marker is only declarative — no plugin consumes it.

### Cross-session race (the issue's primary vector)

`xdist_group` only serializes within a single `pytest -n N` invocation. Two **separate** `pytest` processes (e.g., `whats-next` agent A and agent B both run pytest on the same checkout) are *not* coordinated by xdist. For the cross-session vector, only **per-test source-tree clone (option d done properly)** or an **OS-level filelock** is sufficient.

## Four fix options — scored

| Option | Fix scope | Effort (hr) | Runtime impact (single test) | Correctness | In-session race | Cross-session race |
|---|---|---|---|---|---|---|
| (a) `pytest.mark.xdist_group("wheel-build")` on all three | Add 1-line marker × 3 | 0.25 | 0 (still parallel with non-group tests) | High within session | FIX | NO FIX |
| (b) Drop `--no-isolation` | Edit subprocess args × 3 | 0.5 | +30–60 s/test (PEP 517 venv build per call); 3 tests = +90–180 s | High; loses build-system reuse | FIX (each call gets its own venv) | FIX (build dir is in PEP 517 env, not `<repo_root>/build/`) |
| (c) `@pytest.mark.flaky(reruns=2)` | Install `pytest-rerunfailures` + decorator | 0.5 | 0 on green; 2× on rerun | LOW — hides root cause; flake recurs at higher load | NO FIX (mitigates symptom) | NO FIX (mitigates symptom) |
| (d) Per-test scratch dir = copy source tree to `tmp_path / "src_copy"` and run `python -m build` with `cwd=src_copy` | Add ~10-line helper × 3 | 1.5 | +0.5–2 s/test (source-tree copy; ~2k files) | High; surgical | FIX | FIX (each test owns its own `cwd`) |
| (a)+(d) hybrid | xdist_group + per-test cwd | 1.75 | +0.5–2 s/test | High; defense-in-depth | FIX | FIX |

## Decision

**Adopt option (d) as the primary fix; add option (a) as a belt-and-suspenders.**

Rationale:
1. **(d) alone fixes both vectors** (in-session and cross-session) because each invocation owns its own `cwd` and therefore its own `build/`, `*.egg-info/`, and `dist/`. The "shared workspace" disappears entirely.
2. **(a) is cheap insurance** — `@pytest.mark.xdist_group("digitalmodel-wheel-build")` is a 1-line annotation, costs nothing on green runs, and serializes the trio within a single `pytest -n auto` invocation. Useful if a future contributor adds a fourth wheel-build test that forgets to use `tmp_path` cwd.
3. **Reject (b)**: 90–180 s added to a `pytest -n auto` run that already includes these three tests is a real CI tax. Issue body recommends (b) "for correctness" but the correctness gain over (d) is zero — both eliminate the shared-state race.
4. **Reject (c)** outright: per workspace-hub feedback log entry "no_shortcuts_knowledge", retrying a flake without root-cause is the dispreferred pattern. The issue body itself ranks it last.

### Tradeoff acknowledgement

Option (d) costs ~0.5–2 s per test for the source-tree copy. Acceptable: the test already takes 33–110 s (per issue body). Marginal slowdown <2%.

## Files to change

1. `digitalmodel/tests/naval_architecture/test_rudder_stock_torque_sweep.py` — line ~180 — primary fix target per issue.
2. `digitalmodel/tests/naval_architecture/test_yaw_moment_sweep.py` — line ~135 — sibling collider (issue body confirms).
3. `digitalmodel/tests/naval_architecture/test_turning_circle_estimator.py` — line ~112 — third collider (issue does not mention; missing this regresses the fix).
4. `digitalmodel/tests/naval_architecture/conftest.py` (NEW or extend) — shared `wheel_build_workspace(tmp_path, repo_root)` fixture that:
   - Copies `<repo_root>/src/`, `<repo_root>/pyproject.toml`, `<repo_root>/README.md`, `<repo_root>/MANIFEST.in` (if present), and `<repo_root>/setup.py`/`setup.cfg` (if present) into `tmp_path / "src_copy"`.
   - Returns the path; tests use it as `cwd` for the build invocation.
   - Uses `shutil.copytree(..., ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache", "build", "dist", "*.egg-info"))` to avoid recursive bloat.

5. NO change to `pyproject.toml` dev-deps (no plugin install needed; xdist already present).
6. NO change to `pytest.ini` / `Makefile`.

### Marker addition (option a layer)

```python
@pytest.mark.xdist_group("digitalmodel-wheel-build")
def test_packaged_yaml_in_built_distribution_preserves_existing_package_data(...):
    ...
```

Add the marker to all three sibling tests. Register `xdist_group` in `pytest.ini:markers` if `--strict-markers` rejects it (verify before commit; xdist usually self-registers).

## TDD strategy

A flake under load is hard to TDD with a unit test. Use a **stress-test gate** as the acceptance witness instead:

### Pre-fix repro (red gate)

```bash
# In a fresh shell, FROM digitalmodel/:
uv run pytest -n 4 \
  tests/naval_architecture/test_rudder_stock_torque_sweep.py::test_packaged_yaml_in_built_distribution_preserves_existing_package_data \
  tests/naval_architecture/test_yaw_moment_sweep.py::test_packaged_yaml_in_built_distribution \
  tests/naval_architecture/test_turning_circle_estimator.py::test_packaged_yaml_in_built_distribution \
  --count=10
```

Requires `pytest-repeat` (already transitively available via xdist usage patterns; if not, install `pytest-repeat` for the gate run only — not as a test-time dep). Expect ≥ 1 failure on current `main`.

**NOTE:** This plan does NOT execute the stress-test as part of planning. The gate runs only after implementation. Issue body already confirms the flake is reproducible.

### Post-fix green gate (acceptance)

Same command must pass 30/30 (10 reps × 3 tests) under `-n 4`. Plus:

```bash
# Cross-session race simulation:
( uv run pytest tests/naval_architecture/test_yaw_moment_sweep.py & ) ; \
  uv run pytest tests/naval_architecture/test_rudder_stock_torque_sweep.py
wait
```

Both must exit 0.

## Acceptance criteria

- [ ] All three `test_packaged_yaml_in_built_distribution*` tests pass 30/30 under `pytest -n 4 --count=10` on ace-linux-1.
- [ ] Cross-session simulation (two parallel `pytest` invocations on the same checkout) passes 5/5.
- [ ] Solo-run wall time of `test_packaged_yaml_in_built_distribution_preserves_existing_package_data` is within +50 % of the pre-fix baseline (issue body cites 33–110 s; budget is ≤ 165 s).
- [ ] No new test-time runtime deps (xdist already present; no rerunfailures).
- [ ] `<repo_root>/build/` and `<repo_root>/dist/` are NOT touched by any of the three tests after the fix lands (verified by `inotifywait` or by `mtime` snapshot before/after).
- [ ] `xdist_group("digitalmodel-wheel-build")` marker registered (if needed) and applied to all three.

## Risks

1. **Source-tree copy performance** — `src/` may grow; copying 50 MB per test × 3 tests under `-n 4` could spike I/O. Mitigation: `shutil.copytree` with explicit ignore patterns; if too slow, fall back to symlink-tree (`os.symlink` for files outside `digitalmodel/` data dir) or hardlink (`shutil.copytree(..., copy_function=os.link)` on same FS).
2. **`--no-isolation` semantics rely on the build env** — copying source out of repo means `pyproject.toml` references like `[tool.uv.sources] assetutilities = { path = "../assetutilities", editable = true }` may break (relative path no longer resolves from `tmp_path/src_copy`). **Mitigation:** the build subprocess uses `--with build --with setuptools --with wheel` and `--no-isolation` against the existing uv venv; setuptools reads `pyproject.toml` for project metadata only, not for uv sources. Verify by single-test smoke run before claiming fix complete.
3. **`xdist_group` marker may need explicit registration** in `pytest.ini` because `--strict-markers` is set (`pytest.ini:36`). xdist usually self-registers, but verify on first failed run.
4. **Three test files diverging again** — future fourth wheel-build test could re-introduce the race. Mitigation: the shared `wheel_build_workspace` fixture in `conftest.py` is the canonical entry point; document at fixture-docstring level that any new wheel-build test MUST use it.

## Out of scope

- Refactoring the three tests into a single parametrized test (worth doing, but separate issue).
- Replacing `subprocess.run([...build...])` with `build` Python API (would also fix the race, but bigger surface change).
- Changing `Makefile:23` from `--dist loadscope` to anything else.

## TODO checklist

- [ ] Add `wheel_build_workspace` fixture to `tests/naval_architecture/conftest.py` (or create new file).
- [ ] Update three test functions to use the fixture as `cwd`.
- [ ] Add `@pytest.mark.xdist_group("digitalmodel-wheel-build")` to all three.
- [ ] If `--strict-markers` rejects, register `xdist_group` in `pytest.ini:markers`.
- [ ] Run stress-test gate (above) and confirm 30/30 green.
- [ ] Update issue #2617 with verdict + close.
