# Plan for #2451: worldenergydata test job still fails after #2433 — benchmark fixture + legacy NPV API regressions

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-22
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2451
> **Parent execution issue:** #2433 (collection-unblock, landed at worldenergydata `0f8ac026`)
> **Parent meta issue:** #2424 (ecosystem CI health)
> **Sibling follow-up:** #2452 (flake8 debt keeping `lint` job red)
> **Review artifacts:** `scripts/review/results/20260422T101244Z-2026-04-22-issue-2451-worldenergydata-test-followup.md-plan-claude.md` | `...-codex.md` | `...-gemini.md`

---

## Resource Intelligence Summary

### Existing repo code (worldenergydata at `nightly/2433-worldenergydata`, HEAD `0f8ac026`)

- Found: `worldenergydata/src/worldenergydata/bsee/analysis/production_api12.py` — post-refactor class `ProductionAPI12Analysis` (line 26). The docstring at line 37 explicitly says *"For revenue and NPV calculations, use the financial module at..."* and the class no longer contains `perform_npv_calculation`, `generate_revenue_table`, or `_npv_calculator`.
- Found: `worldenergydata/src/worldenergydata/bsee/analysis/legacy/production_api12_original.py` — pre-refactor copy retains all NPV helpers: `generate_revenue_table` (line 344), `perform_npv_calculation` (line 350), `perform_excel_aligned_npv_calculation` (line 354), and the delegating `_npv_calculator.perform_npv_calculation` call at line 216. This file is under `legacy/` and should not be treated as the canonical API.
- Found: `worldenergydata/tests/benchmarks/test_eia_benchmarks.py` lines 61 and 69 — two tests request the `benchmark` fixture from `pytest-benchmark`. Live pytest reports `fixture 'benchmark' not found`; loaded plugins are `anyio, asyncio, cov, timeout, hypothesis, Faker, dash` — no `benchmark` plugin.
- Found: `worldenergydata/tests/modules/bsee/analysis/npv-data-source-comparison/test_cash_flow_components.py` — the `config_with_economics` fixture is defined at line 105, inside class `TestCashFlowComponents` (line 31). The file also imports from the non-existent path `worldenergydata.modules.bsee.analysis.production_api12` at lines 20–23, but does so inside a `try/except ImportError` block, so the module still collects. It is consumed by two distinct classes:
  - class `TestCashFlowComponents` (methods at lines 140, 164, 316, 388) — can see the fixture
  - class `TestProductionAPI12CashFlowMethods` (line 447, test at line 455) — **cannot see the fixture** (class-scoped fixtures do not cross class boundaries)
  This distinction matters: Cluster B should keep `TestCashFlowComponents` alive while surgically skipping or repointing only the legacy-API class in Cluster C.
- Found: `worldenergydata/tests/modules/bsee/analysis/npv-data-source-comparison/test_current_npv_implementation.py:23` — `from worldenergydata.modules.bsee.analysis.production_api12 import (ProductionAPI12Analysis)`. This import path does not exist on main; the real path is `worldenergydata.bsee.analysis.production_api12` (no `.modules` prefix).
- Found: `worldenergydata/pyproject.toml`
  - Line 60–75 `[project.optional-dependencies] dev = [...]` — contains `"pytest-benchmark>=4.0"` (line 68).
  - Line 213–216 `[dependency-groups] benchmark = [...]` — contains `"pytest-benchmark>=4.0.0,<5.0.0"` (line 215). This is PEP 735 dependency-group declaration.
- Found: `worldenergydata/.github/workflows/ci.yml` — `test` job installs via `uv sync --all-extras` (line 38) and runs `uv run pytest tests/ -v --tb=short --cov=src ...`. `--all-extras` should already install the `dev` extra that declares `pytest-benchmark`.
- Found: local provenance check on `/mnt/local-analysis/worktrees/worldenergydata-2433` after `uv run --all-extras ...` — `pytest_benchmark` imports successfully from `.venv/lib/python3.11/site-packages/pytest_benchmark/__init__.py`. This means the earlier missing-fixture local repro came from an env that had not been proven to match the CI install path, so Cluster A must default to plugin-loading diagnosis (A1b) unless the failing CI log proves the package is absent on runner.
- Found: `worldenergydata/tests/conftest.py` lines 317–376 — the `pytest_ignore_collect` hook extended under #2433 to skip 22 collection-error paths. The three #2451 failure paths are **not** in that skip list and are therefore collected and executed.
- Gap: no shared conftest at `worldenergydata/tests/modules/bsee/analysis/npv-data-source-comparison/conftest.py` — `config_with_economics` cannot be promoted without creating one or moving it up the tree.
- Gap: the refactored `bsee/analysis/production_api12` no longer exposes NPV methods; a "financial module" is referenced in the docstring but its actual path must be confirmed at implementation time (likely `src/worldenergydata/bsee/analysis/financial/` or `src/worldenergydata/financial/`).

### Standards

Not applicable — this is CI / test-hygiene remediation, not an engineering-calculation issue.

### LLM Wiki pages consulted

No relevant wiki pages — this is a cross-repo test-drift issue.

### Documents consulted

- Issue #2451 body (workspace-hub) — scope: runtime-test layer only after #2433 collection unblock; three representative clusters listed.
- Issue #2433 body and execution comment `4293256122` (workspace-hub) — precedent plan, Path-1 decision framework, and residual-blocker enumeration referencing run `24757842396`.
- Issue #2452 (workspace-hub, sibling) — separate `lint` job flake8 debt, explicitly out of scope for #2451.
- `docs/plans/2026-04-21-issue-2433-worldenergydata-ci.md` — parent plan template for worldenergydata CI remediation. Re-uses conftest skip-list mechanism and adversarial-review loop.
- `docs/plans/_template-issue-plan.md` — canonical template; sections and evidence contract inherited verbatim.
- `docs/plans/README.md` — plan index (intentionally **not** edited in this run per branch-contention guard).

### Gaps identified

- No skip/xfail path exists today for the three #2451 clusters — current state is hard runtime failure across Python 3.10 / 3.11 / 3.12 matrix.
- The "financial module" for NPV calculations is referenced in the production-code docstring but its concrete API surface and path are not confirmed in this planning pass. Implementation must do a live grep before committing to a repoint-based fix.
- No prior plan in `docs/plans/` addresses the test-drift between `worldenergydata.modules.bsee.*` (legacy) and `worldenergydata.bsee.*` (current) import namespaces.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-22T09:45Z via `gh issue view`):
- `#2451` — OPEN — `follow-up(ci): worldenergydata test job still fails after #2433 collection fix — benchmark fixture + legacy NPV API regressions` — labels: `priority:medium`, `cat:infrastructure`
- `#2433` — OPEN — parent execution issue, `status:plan-approved`, `priority:high`
- `#2452` — referenced in #2433 comment `4295180987` as flake8 sibling follow-up
- `#2424` — parent ecosystem meta-issue (referenced in #2433 body)

**CI run** (from #2451 body and #2433 comment `4293256122`):
- worldenergydata run `24757842396` on SHA `0f8ac026`
- `Test Python 3.11` job: collection green (11872 tests), runtime layer red on the three clusters below

**File existence** (`ls -la` 2026-04-22 inside `/mnt/local-analysis/worktrees/worldenergydata-2433`):
- EXISTS: `tests/benchmarks/test_eia_benchmarks.py`
- EXISTS: `tests/modules/bsee/analysis/npv-data-source-comparison/test_cash_flow_components.py`
- EXISTS: `tests/modules/bsee/analysis/npv-data-source-comparison/test_current_npv_implementation.py`
- EXISTS: `src/worldenergydata/bsee/analysis/production_api12.py` (refactored, no NPV methods)
- EXISTS: `src/worldenergydata/bsee/analysis/legacy/production_api12_original.py` (has `perform_npv_calculation`)
- MISSING (this is the import the tests expect): `src/worldenergydata/modules/bsee/analysis/production_api12.py` — confirms the import path `worldenergydata.modules.bsee.analysis.production_api12` cannot resolve.
- MISSING: `tests/modules/bsee/analysis/npv-data-source-comparison/conftest.py` — no shared-fixture anchor exists.

**Live benchmark failure** (`uv run pytest tests/benchmarks/test_eia_benchmarks.py -v --tb=short --override-ini="addopts="` 2026-04-22):
```
plugins: anyio-4.11.0, asyncio-1.2.0, cov-7.0.0, timeout-2.4.0, hypothesis-6.151.0, Faker-37.8.0, dash-2.18.2
...
E       fixture 'benchmark' not found
...
ERROR tests/benchmarks/test_eia_benchmarks.py::test_bench_state_production_loader
ERROR tests/benchmarks/test_eia_benchmarks.py::test_bench_basin_production_loader
============================== 2 errors in 3.12s ===============================
```
The plugin list contains no `benchmark` entry, confirming `pytest-benchmark` is not installed even though it is declared in `[project.optional-dependencies] dev` and `[dependency-groups] benchmark`.

**Fixture-scope evidence** (`grep -n "^class\|@pytest.fixture\|def test_" tests/modules/bsee/analysis/npv-data-source-comparison/test_cash_flow_components.py`):
```
31:class TestCashFlowComponents:
34:    @pytest.fixture
74:    @pytest.fixture
105:    @pytest.fixture          # <-- config_with_economics
119:    def test_revenue_calculation_basic
140:    def test_opex_calculation_basic                       (needs config_with_economics — SAME class, OK)
164:    def test_net_cash_flow_calculation                    (needs config_with_economics — SAME class, OK)
316:    def test_cash_flow_dataframe_structure                (needs config_with_economics — SAME class, OK)
388:    def test_cash_flow_with_capex_period_zero             (needs config_with_economics — SAME class, OK)
447:class TestProductionAPI12CashFlowMethods:
455:    def test_revenue_table_generation_structure          (needs config_with_economics — DIFFERENT class, FAILS)
```

**Legacy API evidence** (`grep -n "perform_npv_calculation\|def " src/worldenergydata/bsee/analysis/legacy/production_api12_original.py`):
```
344:    def generate_revenue_table(self, cfg, api12_df):
347:        self._npv_calculator.perform_npv_calculation(cfg, revenue_df)
350:    def perform_npv_calculation(self, cfg, revenue_df):
352:        return self._npv_calculator.perform_npv_calculation(cfg, revenue_df)
354:    def perform_excel_aligned_npv_calculation(self, cfg, revenue_df):
```
Refactored file (`src/worldenergydata/bsee/analysis/production_api12.py`) contains only production-analysis methods (`router`, `run_production_analysis`, `analyze_data_for_api12`, `perform_decline_analysis_api12`, plot helpers). Line 37 docstring: *"For revenue and NPV calculations, use the financial module at..."*.

**CI install path** (`.github/workflows/ci.yml` lines 36–48):
```yaml
- name: Install dependencies
  run: uv sync --all-extras
- name: Run tests with coverage
  run: |
    uv run pytest tests/ \
      -v --tb=short --cov=src ...
```
`--all-extras` installs `[project.optional-dependencies]`, which already includes `pytest-benchmark` via the `dev` extra. Therefore Cluster A cannot treat `--all-groups` as the default fix until the failing CI log proves the runner is specifically missing the benchmark plugin. Implementation must first inspect the failing job log on run `24757842396` and choose among explicit branches:
- **A1a**: if CI truly shows `fixture 'benchmark' not found` and the runner is not installing the relevant dependency-group, test-job-only workflow change (`--all-extras --group benchmark` or `--all-extras --all-groups`, depending runner `uv` support)
- **A1b**: if the package is installed but the plugin still is not available, diagnose plugin autoload / environment-isolation cause before editing ci.yml
- **A2**: fallback test-local skip only if the CI/plugin diagnosis shows the workflow edit would be a no-op or wider than this issue's scope
This plan therefore keeps Cluster A conditional rather than pre-selecting a workflow edit as the universal preferred path.

<!-- Verification: 6 distinct sources — (1) issue #2451 body, (2) issue #2433 execution comment, (3) worldenergydata repo code at SHA 0f8ac026, (4) worldenergydata pyproject.toml, (5) worldenergydata ci.yml, (6) live pytest reproduction. Minimum 3 required. Current count: 6 -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-22-issue-2451-worldenergydata-test-followup.md` |
| Plan review — Claude | `scripts/review/results/20260422T101244Z-2026-04-22-issue-2451-worldenergydata-test-followup.md-plan-claude.md` |
| Plan review — Codex | `scripts/review/results/20260422T101244Z-2026-04-22-issue-2451-worldenergydata-test-followup.md-plan-codex.md` |
| Plan review — Gemini | `scripts/review/results/20260422T101244Z-2026-04-22-issue-2451-worldenergydata-test-followup.md-plan-gemini.md` |
| Implementation (cluster A) | `worldenergydata/.github/workflows/ci.yml` (`test` job install step only, and only if CI log proves plugin absence) **or** `worldenergydata/tests/benchmarks/test_eia_benchmarks.py` (fallback skip if workflow edit would be a no-op) |
| Implementation (cluster B) | `worldenergydata/tests/modules/bsee/analysis/npv-data-source-comparison/conftest.py` (promote fixture verbatim from current class fixture) |
| Implementation (cluster C) | `worldenergydata/tests/modules/bsee/analysis/npv-data-source-comparison/test_current_npv_implementation.py` (collection-safe module skip or repoint) + `test_cash_flow_components.py` (class-level skip on `TestProductionAPI12CashFlowMethods` only, or repoint) |
| Plan index | `docs/plans/README.md` (row added in a later, separate run — not this PR per branch-contention guard) |

---

## Deliverable

The worldenergydata `Test Python ${version}` CI jobs (3.10 / 3.11 / 3.12) will complete without the three failure clusters enumerated in #2451 — either by installing the missing benchmark plugin on CI, repointing imports to the refactored financial module, and promoting `config_with_economics` to shared fixture scope (fix-now path), **or** by cleanly skipping the affected tests with explicit tracking (xfail/skip path). The final `Test` job status after this plan executes will be either (a) green, or (b) materially reduced residual failure count with each remaining failure traceable to a follow-up issue. Plan #2452 remains responsible for the `Lint` job flake8 debt independently.

---

## Pseudocode

```
# === TDD Phase: lock the RED baseline before any edits ===

# Step 0 (RED): confirm each cluster reproduces locally before touching code
cd worldenergydata/
uv run pytest tests/benchmarks/test_eia_benchmarks.py --override-ini="addopts=" \
    | grep -E "fixture 'benchmark' not found|ERROR tests/benchmarks"
uv run pytest tests/modules/bsee/analysis/npv-data-source-comparison/test_cash_flow_components.py \
    --override-ini="addopts=" \
    | grep -E "fixture 'config_with_economics' not found|ERROR"
uv run pytest tests/modules/bsee/analysis/npv-data-source-comparison/test_current_npv_implementation.py \
    --override-ini="addopts=" --collect-only \
    | grep -E "ModuleNotFoundError|ImportError"

# Step 0b: confirm CI install-time reality — pull latest failing job log
#   gh run view <run_id> --repo vamseeachanta/worldenergydata --log-failed \
#       | grep -A5 "fixture 'benchmark' not found"
#
# Step 0c: establish local provenance against the CI-style install path.
#   uv run --all-extras python - <<'PY'
#   import pytest_benchmark
#   print(pytest_benchmark.__file__)
#   PY
# If pytest_benchmark imports locally after `--all-extras`, the local missing-fixture
# repro was a stale-env artifact and Cluster A should start from A1b (plugin loading),
# not from an install-layer workflow edit.

# === Cluster A — benchmark fixture ===
# This branch is CONDITIONAL. Do not edit ci.yml until the failing CI log proves
# the runner is actually missing the benchmark plugin.
#
# Step A0: inspect the failing CI log on run 24757842396 for the exact signature.
#   gh run view 24757842396 --repo vamseeachanta/worldenergydata --log-failed \
#       | grep -A5 -B2 "fixture 'benchmark' not found"
#
# Step A0b: inspect the runner/install evidence.
#   - if install log or env proof shows pytest-benchmark is absent on the runner,
#     proceed to A1a.
#   - if pytest-benchmark is installed but the fixture still is not available,
#     stop and re-scope to A1b (plugin autoload / environment isolation diagnosis).
#
# Branch A1a (bounded workflow fix, test job only):
# Edit ONLY the `test` job install step in .github/workflows/ci.yml to guarantee
# benchmark deps are present on the runner, but only if failed-job log evidence
# shows the package is actually absent there. Prefer the narrowest flag the
# runner's uv version supports:
#   run: uv sync --all-extras --group benchmark
# or, if needed and supported:
#   run: uv sync --all-extras --all-groups
#
# Branch A1b (diagnose plugin-loading bug, preferred starting branch):
# If CI already has pytest-benchmark installed, investigate plugin autoload
# suppression (`PYTEST_DISABLE_PLUGIN_AUTOLOAD`, `-p no:...`, custom pytest config)
# before changing ci.yml. Because local `uv run --all-extras` already imports
# pytest_benchmark successfully, this is the default branch unless CI logs prove
# the runner is missing the package.
#
# Branch A2 (fallback, defer): skip benchmark tests when plugin diagnosis shows
# the workflow edit is a no-op or too broad for this issue.
# Add a module-top bare importorskip:
#   pytest.importorskip("pytest_benchmark")
#
# Decision rule: start from A1b by default. Use A1a only after the CI log proves
# the missing-fixture error is truly caused by absent benchmark plugin availability
# on the runner.

# === Cluster B — config_with_economics fixture scope ===
# Option B1 (preferred): create tests/modules/bsee/analysis/npv-data-source-comparison/conftest.py
#   with the fixture at module scope so BOTH TestCashFlowComponents and
#   TestProductionAPI12CashFlowMethods can consume it.
# IMPORTANT: copy the existing fixture body from lines 105-117 verbatim.
# conftest.py contents should preserve the current values exactly:
#   CAPEX = 1460000000
#   OPEX_per_bbl = 20.0
#   discount_rate_annual = 0.10
#   meta.label = "test_cash_flow"
# Then remove the in-class fixture at line 105 of test_cash_flow_components.py
# to avoid a duplicate-definition warning.
#
# Before editing, verify there are no additional consumers beyond the two known
# classes by grepping the directory for `config_with_economics`.
#
# Option B2 (minimal): duplicate the fixture inside TestProductionAPI12CashFlowMethods.
# Rejected — creates drift between classes; B1 is the cleaner fix.

# === Cluster C — legacy NPV API / import-path drift ===
# The tests reference legacy `worldenergydata.modules.bsee.analysis.production_api12`
# and/or `perform_npv_calculation`, which the refactored code no longer exposes.
# Use collection-safe handling that does NOT accidentally skip unrelated tests.
#
# Sub-path C-repoint (keep tests): repoint imports to the new path and call site
#   - Grep the repo for the post-refactor NPV entry point
#       (likely under src/worldenergydata/bsee/analysis/financial/ or
#        src/worldenergydata/financial/)
#   - Update the two test files' imports and method calls to the new API signature
#   - Update assertions if the return shape changed
#
# Sub-path C-skip (track-and-move-on, default):
#   - In test_current_npv_implementation.py, prevent collection-time failure with
#     a module-level `pytest.skip(..., allow_module_level=True)` placed before the
#     broken legacy import.
#   - In test_cash_flow_components.py, keep TestCashFlowComponents active for
#     Cluster B, and apply a class-level `pytestmark = pytest.mark.skip(...)`
#     only to `TestProductionAPI12CashFlowMethods`, which is the legacy-API
#     consumer that currently fails.
#   - Every skip reason must reference #2451 explicitly.
#
# Sub-path C-delete (aggressive): remove the two files entirely.
#   - Rejected as default because test-preservation is cheaper than
#     test-rewriting if the decision is later reversed.
#
# Recommended default: C-skip, but implemented surgically and collection-safely.
# This preserves Cluster B coverage while deferring the refactor decision to the
# module owner.

# === Verification Phase (GREEN) ===

# Step V1: re-run each cluster's pytest command from Step 0 and confirm the
# exact three #2451 failure signatures are gone (either PASSED or SKIPPED,
# not ERROR):
#   - no `fixture 'benchmark' not found`
#   - no `fixture 'config_with_economics' not found`
#   - no `ModuleNotFoundError` / missing `perform_npv_calculation` from the
#     two legacy NPV targets targeted by Cluster C
# Step V1a: prove Cluster B at runtime, not just collection:
#   uv run pytest tests/modules/bsee/analysis/npv-data-source-comparison/test_cash_flow_components.py::TestCashFlowComponents::test_opex_calculation_basic -v --override-ini="addopts="
#   uv run pytest tests/modules/bsee/analysis/npv-data-source-comparison/test_cash_flow_components.py::TestProductionAPI12CashFlowMethods::test_revenue_table_generation_structure -v --override-ini="addopts="
# Expected: first test PASSES; second test is SKIPPED (C-skip) or PASSES (C-repoint), but does not error on missing fixture.
# Step V2: run the full CI command locally:
#   uv run pytest tests/ -v --tb=short --cov=src
# Expected: the three #2451 clusters are eliminated from the failure surface.
# Other unrelated residual failures may remain, but they must be enumerated as
# outside this issue's scope, not counted as satisfying the three-cluster fix.
# Step V3: push the fix branch and confirm the matrix job on run <new_id>
# at worldenergydata SHA <new_sha>.
# Step V4: re-run `uv run pytest tests/ --collect-only --override-ini="addopts="`
# to ensure no new collection failures were introduced by the fixture/skip edits.
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify (conditional) | `worldenergydata/.github/workflows/ci.yml` | (Cluster A1a only) narrow workflow edit on the `test` job install step if and only if CI-log evidence proves the runner is missing the benchmark plugin. Prefer `uv sync --all-extras --group benchmark`; fall back to `--all-groups` only if required by runner/tooling. `lint` job stays untouched — #2452 owns that lane. |
| Create | `worldenergydata/tests/modules/bsee/analysis/npv-data-source-comparison/conftest.py` | (Cluster B1) module-scope `config_with_economics` fixture copied verbatim from the current in-class fixture so both `TestCashFlowComponents` and `TestProductionAPI12CashFlowMethods` can consume it. |
| Modify | `worldenergydata/tests/modules/bsee/analysis/npv-data-source-comparison/test_cash_flow_components.py` | (Cluster B1) remove now-redundant in-class fixture at line 105 after promotion to conftest; (Cluster C default) apply class-level skip only to `TestProductionAPI12CashFlowMethods` if the legacy API is deferred, preserving `TestCashFlowComponents` coverage. |
| Modify | `worldenergydata/tests/modules/bsee/analysis/npv-data-source-comparison/test_current_npv_implementation.py` | (Cluster C default) add collection-safe module-level `pytest.skip(..., allow_module_level=True)` before the broken legacy import, or repoint to the refactored financial module if the owner chooses C-repoint. |
| Modify (fallback only) | `worldenergydata/tests/benchmarks/test_eia_benchmarks.py` | Only if Cluster A2 is chosen after CI-log diagnosis. Use bare `pytest.importorskip("pytest_benchmark")` at module top. |
| Update (deferred, not this run) | `docs/plans/README.md` | Plan index row. Intentionally **not** edited in the nightly/2451-plan branch per the branch-contention guard — performed in a later consolidation run. |

---

## TDD Test List

This is a cross-repo infrastructure / test-hygiene fix. "Tests" here are verification commands executed against the `worldenergydata` clone; no new pytest files in workspace-hub.

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| verify_benchmark_cluster_resolved | `uv run pytest tests/benchmarks/test_eia_benchmarks.py --override-ini="addopts="` no longer reports `fixture 'benchmark' not found` | worldenergydata with A1a (or A2) applied | Exit code 0 for A1a (tests pass) or SKIPPED line for A2 |
| verify_benchmark_root_cause_confirmed | `gh run view 24757842396 --repo vamseeachanta/worldenergydata --log-failed | grep -c "fixture 'benchmark' not found"` plus install-log inspection | failing CI run | >0 only if Cluster A workflow change is justified; otherwise branch to A1b/A2 |
| verify_local_all_extras_provenance | `uv run --all-extras python -c "import pytest_benchmark; print(pytest_benchmark.__file__)"` | worldenergydata local env | Import succeeds or clearly fails with provenance recorded before choosing A1a vs A1b |
| verify_cashflow_fixture_consumers | `rg -n "config_with_economics" tests/modules/bsee/analysis/npv-data-source-comparison/` | pre-fix tree | only the expected fixture definition + consumer references are present |
| verify_cashflow_fixture_runtime_primary | `uv run pytest tests/modules/bsee/analysis/npv-data-source-comparison/test_cash_flow_components.py::TestCashFlowComponents::test_opex_calculation_basic -v --override-ini="addopts="` | worldenergydata with B1 applied | PASS |
| verify_cashflow_fixture_runtime_legacy_class | `uv run pytest tests/modules/bsee/analysis/npv-data-source-comparison/test_cash_flow_components.py::TestProductionAPI12CashFlowMethods::test_revenue_table_generation_structure -v --override-ini="addopts="` | worldenergydata with B1 + C handling | SKIPPED (C-skip) or PASS (C-repoint), but never fixture-missing ERROR |
| verify_cashflow_no_duplicate_fixture | Grep for `def config_with_economics` in the test file after edit | post-edit file | Exactly 0 hits in `test_cash_flow_components.py` (fixture only in conftest) |
| verify_current_npv_collection_safe | `uv run pytest tests/modules/bsee/analysis/npv-data-source-comparison/test_current_npv_implementation.py --collect-only --override-ini="addopts="` | worldenergydata with C-skip or C-repoint | No import-time collection error; file is either skipped or collects cleanly |
| verify_ci_residual_failure_set | `uv run pytest tests/ -v --tb=short --cov=src` | full CI command | The three #2451 failure signatures are absent; any remaining failures are explicitly outside this issue's scope |
| verify_ci_matrix_effect | New worldenergydata CI run on the fix SHA shows the three #2451 clusters gone from the `Test Python 3.11` job | `gh run view <id>` | No benchmark-fixture, `config_with_economics`, or legacy-NPV-import/method errors remain |

---

## Acceptance Criteria

- [ ] Exact CI command `uv run pytest tests/ -v --tb=short --cov=src` in the worldenergydata clone no longer reports the three failure signatures from the #2451 body: (1) benchmark fixture missing, (2) `config_with_economics` fixture missing, (3) legacy NPV import / missing `perform_npv_calculation` failures.
- [ ] Cluster A branch is chosen only after failed-job log inspection on run `24757842396` confirms the benchmark root cause. Local provenance is also checked with `uv run --all-extras` before choosing A1a vs A1b. If a workflow edit is made, it is scoped to the `test` job only; `lint` remains untouched for #2452.
- [ ] `worldenergydata/tests/modules/bsee/analysis/npv-data-source-comparison/conftest.py` exists and defines `config_with_economics` at module scope using the same values as the current in-class fixture.
- [ ] `test_cash_flow_components.py` no longer contains an in-class `config_with_economics` fixture definition after the edit (no duplicate shadowing).
- [ ] Cluster B is proven at runtime, not just collection: a representative `TestCashFlowComponents` test passes and the legacy class test is either skipped cleanly or passes after repoint.
- [ ] Cluster C handling is collection-safe: `test_current_npv_implementation.py` no longer errors during collection, and `test_cash_flow_components.py` preserves `TestCashFlowComponents` coverage while only the legacy-API class is skipped or repointed.
- [ ] No file under the #2433 conftest skip-set is re-introduced to the collection surface by accident (re-run `uv run pytest tests/ --collect-only --override-ini="addopts="` still reports 0 collection errors).
- [ ] A worldenergydata CI run on the fix SHA shows the three #2451 failure clusters gone from the `Test` job. Remaining failures, if any, are explicitly enumerated as unrelated follow-up work rather than counted toward this issue.
- [ ] Adversarial review of this plan across ≥ 2 providers returns APPROVE or MINOR after final revisions.
- [ ] `status:plan-review` label applied on #2451, with the plan comment linking this file and its review artifacts. User approval and `.planning/plan-approved/2451.md` marker remain workflow gates before any implementation commit, not deliverable proof.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MAJOR | Required class-surgical handling in `test_cash_flow_components.py`, conditional Cluster A decisioning, concrete import evidence for that file, fixture-body preservation, and separation of planning-process gates from deliverable acceptance. |
| Codex | MAJOR | Required Cluster A to stop treating workflow edits as preferred-by-default, required collection-safe Cluster C skip strategy, and tightened acceptance around the exact three failure signatures. |
| Gemini | APPROVE | Minor caution on `--all-groups` breadth and uv-version support; no blocking defects beyond the other providers' findings. |

**Wave 2 overall result:** MAJOR — Claude and Codex narrowed the remaining defects to execution-contract inconsistencies: Cluster B needed runtime verification rather than collect-only, and the Path Decision Summary still contradicted the body on Cluster A and Cluster C. The draft has now been updated to (1) add local provenance proving `pytest_benchmark` imports after `uv run --all-extras`, which shifts Cluster A's default starting branch to plugin-loading diagnosis (A1b), (2) replace Cluster B's collect-only proof with explicit runtime tests from both affected classes, (3) reconcile the Path Decision Summary with the body's class-surgical Cluster C handling and conditional Cluster A logic, and (4) update artifact paths to the concrete Wave 2 review files.

Revisions made based on review:
- Replaced review-artifact placeholders in the Artifact Map with the concrete Wave 2 filenames.
- Added local provenance evidence showing `pytest_benchmark` imports successfully after `uv run --all-extras`, so a stale env — not proven CI install failure — explains the earlier local benchmark repro.
- Added Step 0c to the pseudocode to prove local provenance before choosing Cluster A branch.
- Changed Cluster A default starting branch to A1b (plugin-loading diagnosis), with A1a only after CI log evidence proves package absence on runner.
- Replaced Cluster B collect-only proof with explicit runtime verification of one primary-class test and one legacy-class test outcome.
- Will reconcile the Path Decision Summary in the next revision so Cluster A and Cluster C wording matches the body exactly.
- Clarified that `.planning/plan-approved/2451.md` is a workflow gate before implementation, not a deliverable proof item.

---

## Risks and Open Questions

- **Risk — wrong root cause for Cluster A.** The local reproduction confirms the fixture is missing, but the local `.venv` may not have been synced with `--all-extras`. Implementation must pull the worldenergydata CI job log for run `24757842396` (Python 3.11 matrix) and confirm that the same `fixture 'benchmark' not found` error appears there. If CI already installs `dev` extras and still misses the fixture, the root cause is different (plugin load order, duplicate declaration conflict, or environment isolation) and Cluster A must be re-scoped before any ci.yml edit.
- **Risk — Cluster B fix surfaces additional test code smells.** Moving `config_with_economics` to a shared conftest may reveal that other consumer classes were relying on class-scoped defaults different from the one in `TestCashFlowComponents`. Re-run the full NPV directory under pytest after the fix and inspect for any test whose assertions silently changed meaning.
- **Risk — Cluster C default (skip) hides real product failures.** If the refactored production code has an NPV regression and the legacy tests were genuinely catching it, skipping is a coverage loss. Mitigation: the skip reason string **must** name #2451 and a follow-up owner must file a new worldenergydata issue tracking "re-enable or delete legacy NPV tests after financial-module audit."
- **Risk — iceberg dynamic.** As with #2433 → #2451, fixing these three clusters may reveal a fourth layer of pre-existing test-health issues (stale reference data, drifted assertion tolerances, env-dependent test skips). The plan's acceptance criteria deliberately permit residual failures traceable to new follow-ups rather than requiring full CI-green on one pass.
- **Risk — cross-branch contention on `docs/plans/README.md`.** Multiple planning branches are being drafted in parallel today. Per the session directive, this plan intentionally does **not** touch the README index. The consolidation edit must be performed in a separate run that merges cleanly after all parallel planning branches are serialized.
- **Open — Cluster C branch decision.** The plan recommends C-skip as default, C-repoint as upgrade, C-delete as rejected. The final choice requires the module owner (vamseeachanta) to weigh the NPV test coverage value against the cost of tracing the refactored financial-module API. Flag for user during plan-review.
- **Open — should a dedicated worldenergydata-side follow-up issue be filed for legacy-test re-enablement?** Recommended (mirrors #2433 conftest re-enablement note), but scope-wise this plan deliberately limits itself to unblocking the exact three clusters from #2451; the re-enablement tracker belongs in a sibling worldenergydata issue rather than here.
- **Open — `uv sync --all-groups` compatibility.** PEP 735 `--all-groups` is supported in recent `uv` versions (≥ 0.4.x); the CI uses `astral-sh/setup-uv@v7` which pins a compatible version. Re-verify before committing that the installed `uv` on the GitHub-hosted runner accepts the flag. If not, fall back to explicit `--group benchmark`.

---

## Complexity: T2

**T2** — cross-repo test-hygiene fix touching up to 4 files in `worldenergydata` (one CI workflow, one new conftest, two test files) with three independent failure clusters that each have at least two implementation branches. Not T1 because branch-selection judgment is required per cluster and CI-log verification is needed before Cluster A can be committed. Not T3 because no architectural decisions, no new modules, no cross-repo API contract changes, and the fix surface is bounded by the three clusters enumerated in #2451.

---

## Path Decision Summary

| Cluster | Preferred path | Rejected paths | Gate |
|---|---|---|---|
| A — benchmark fixture | A1b plugin-loading diagnosis by default; A1a `uv sync --all-extras --group benchmark` only if CI log proves package absence on runner (`--all-groups` fallback only if required) | A2 `importorskip` test-local skip (fallback only) | Failed-job log plus local `uv run --all-extras` provenance must establish whether the runner is missing the package or failing to autoload the plugin |
| B — `config_with_economics` scope | B1 module-scope conftest.py + runtime verification from both affected classes | B2 in-class duplication | None — additive fix, but runtime verification is mandatory |
| C — legacy NPV API drift | C-skip, collection-safe and surgical: module-level skip only in `test_current_npv_implementation.py`, class-level skip only on `TestProductionAPI12CashFlowMethods` in `test_cash_flow_components.py` | C-repoint (requires financial-module audit), C-delete (too aggressive) | User confirmation required during plan-review; C-skip remains the conservative default unless owner prefers restoring coverage now |

This plan explicitly stops short of implementation. Implementation requires `status:plan-approved` on #2451 and a corresponding `.planning/plan-approved/2451.md` marker.
