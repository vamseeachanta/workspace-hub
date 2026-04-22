# Plan for #2451: worldenergydata test job still fails after #2433 — benchmark fixture + legacy NPV API regressions

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-22
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2451
> **Parent execution issue:** #2433 (collection-unblock, landed at worldenergydata `0f8ac026`)
> **Parent meta issue:** #2424 (ecosystem CI health)
> **Sibling follow-up:** #2452 (flake8 debt keeping `lint` job red)
> **Review artifacts:** `scripts/review/results/20260422T110857Z-2026-04-22-issue-2451-worldenergydata-test-followup.md-plan-claude.md` | `...-codex.md` | `...-gemini.md`

---

## Resource Intelligence Summary

### Existing repo code (worldenergydata at `nightly/2433-worldenergydata`, HEAD `0f8ac026`)

- Found: `worldenergydata/src/worldenergydata/bsee/analysis/production_api12.py` — post-refactor class `ProductionAPI12Analysis` (line 26). The docstring at line 37 explicitly says *"For revenue and NPV calculations, use the financial module at..."* and the class no longer contains `perform_npv_calculation`, `generate_revenue_table`, or `_npv_calculator`.
- Found: `rg -n "perform_npv_calculation|perform_excel_aligned_npv_calculation" src/worldenergydata/` on `/mnt/local-analysis/worktrees/worldenergydata-2433` — only legacy hits were found:
  - `src/worldenergydata/bsee/analysis/legacy/production_api12_original.py`
  - `src/worldenergydata/bsee/analysis/legacy/api12_economics.py`
  No non-legacy replacement entry point was identified during planning, so C-repoint remains explicitly blocked on further owner-directed discovery; C-skip is the only approval-safe default today.
- Found: `worldenergydata/tests/benchmarks/test_eia_benchmarks.py` lines 61 and 69 — two tests request the `benchmark` fixture from `pytest-benchmark`. Live pytest reports `fixture 'benchmark' not found`; loaded plugins are `anyio, asyncio, cov, timeout, hypothesis, Faker, dash` — no `benchmark` plugin.
- Found: `worldenergydata/tests/modules/bsee/analysis/npv-data-source-comparison/test_cash_flow_components.py` — the `config_with_economics` fixture is defined at line 105, inside class `TestCashFlowComponents` (line 31). The file also imports from the non-existent path `worldenergydata.modules.bsee.analysis.production_api12` at lines 20–23, but does so inside a `try/except ImportError` block, so the module still collects. It is consumed by two distinct classes:
  - class `TestCashFlowComponents` (methods at lines 140, 164, 316, 388) — can see the fixture and does not independently prove a fixture-scope defect
  - class `TestProductionAPI12CashFlowMethods` (line 447, test at line 455) — **cannot see the fixture** (class-scoped fixtures do not cross sibling class boundaries)
  This distinction matters: if Cluster C uses the default skip on the legacy class, the demonstrated `config_with_economics` failure may disappear without needing immediate fixture promotion. Cluster B therefore remains conditional rather than automatically mandatory.
- Found: `worldenergydata/tests/modules/bsee/analysis/npv-data-source-comparison/test_current_npv_implementation.py` — every test in this file is legacy-API-bound. The module imports `ProductionAPI12Analysis` from the non-existent legacy path at line 23, initializes `self.analyzer = ProductionAPI12Analysis()` in `setup_method` at line 32, and its test methods call or patch `perform_npv_calculation` / the legacy workflow throughout (e.g. lines 78, 104, 251, 292). No non-legacy coverage exists in this file, so a collection-safe module-level skip is proportionate under the default C-skip path.
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
| Plan review — Claude | `scripts/review/results/20260422T110857Z-2026-04-22-issue-2451-worldenergydata-test-followup.md-plan-claude.md` |
| Plan review — Codex | `scripts/review/results/20260422T110857Z-2026-04-22-issue-2451-worldenergydata-test-followup.md-plan-codex.md` |
| Plan review — Gemini | `scripts/review/results/20260422T110857Z-2026-04-22-issue-2451-worldenergydata-test-followup.md-plan-gemini.md` |
| Implementation (cluster A) | `worldenergydata/.github/workflows/ci.yml` (`test` job install step only, and only if CI log proves plugin absence) **or** `worldenergydata/tests/benchmarks/test_eia_benchmarks.py` (fallback skip if workflow edit would be a no-op) |
| Implementation (cluster B) | `worldenergydata/tests/modules/bsee/analysis/npv-data-source-comparison/conftest.py` (promote fixture verbatim from current class fixture) |
| Implementation (cluster C) | `worldenergydata/tests/modules/bsee/analysis/npv-data-source-comparison/test_current_npv_implementation.py` (collection-safe module skip or repoint) + `test_cash_flow_components.py` (class-level skip on `TestProductionAPI12CashFlowMethods` only, or repoint) |
| Plan index | `docs/plans/README.md` (row added in a later, separate run — not this PR per branch-contention guard) |

---

## Deliverable

Primary acceptance lane for #2451 is the worldenergydata `Test Python 3.11` job, because that is the matrix lane directly evidenced in the failing-run investigation. Success means that lane no longer exhibits the three #2451 failure clusters:
1. benchmark-fixture failure,
2. `config_with_economics` fixture-scope failure,
3. legacy NPV import / missing `perform_npv_calculation` failure.

If the same three signatures are also observed on Python 3.10 or 3.12 during execution, those sibling matrix lanes are included in the fix/verification set for this issue as well. Unrelated residual failures may remain only if they are separately enumerated as out-of-scope follow-up work. Plan #2452 remains responsible for the `Lint` job flake8 debt independently.

---

## Pseudocode

```
# === TDD Phase: lock the RED baseline before any edits ===

# Step -2: verify GitHub CLI access before any branch-selection logic that depends on
# CI log inspection or tracker creation.
#   gh auth status
#   gh run view 24757842396 --repo vamseeachanta/worldenergydata --json databaseId,status,conclusion >/dev/null
#   gh issue view 2451 --repo vamseeachanta/workspace-hub >/dev/null
# For skip-based Cluster C, also verify issue-write capability on the target repo at the
# moment of execution by creating the required follow-up tracker before any code edit.
# If `gh` cannot read the worldenergydata run, cannot view the governing workspace-hub
# issue, or cannot create/view the required tracker issue, STOP and do not guess a branch.
# Fallback is not 'continue locally'; fallback is 'pause implementation and return to
# workspace-hub issue #2451 with the missing-GitHub-access blocker documented'.
#
# Step -1: if Cluster C skip-based deferral is the selected path, create the
# required worldenergydata follow-up tracker issue FIRST, capture its issue
# number, and use that concrete number in every skip reason string.
# Recommended title:
#   follow-up(tests): re-enable or delete legacy NPV tests after financial-module audit
# Recommended labels: ci, tests, tech-debt (or repo-standard equivalents)
# This tracker must exist before any skip-based code edit lands.

# Step 0 (RED): confirm each cluster reproduces locally before touching code.
# For Cluster A, the authoritative RED proof is the failing CI log plus local
# provenance, not a mandatory stale-env local failure reproduction.
cd worldenergydata/
uv run pytest tests/benchmarks/test_eia_benchmarks.py --override-ini="addopts=" \
    | grep -E "fixture 'benchmark' not found|ERROR tests/benchmarks" || true
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
#
# Step 0d: locate the post-refactor NPV entry point before C-repoint is selectable.
#   rg -n "def .*npv|perform_npv_calculation|perform_excel_aligned_npv_calculation" src/worldenergydata/
# Record the concrete module path in execution notes. Time-box this discovery to the
# bounded grep/read surface above; if no non-legacy replacement path is identified
# within that bounded pass, C-repoint is blocked and C-skip remains the only
# approval-safe default.

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
# If CI already has pytest-benchmark installed, inspect these bounded surfaces in order:
#   1. pytest configuration in `pytest.ini`, `pyproject.toml`, and `tests/conftest.py`
#      for `addopts`, `pytest_plugins`, or plugin-disabling directives.
#   2. CI workflow env and command lines for `PYTEST_DISABLE_PLUGIN_AUTOLOAD`,
#      `-p no:pytest_benchmark`, wrapper scripts, or custom invocation layers.
#   3. Any test-local plugin filtering that affects benchmark fixture registration.
#   4. Duplicate declaration interaction between `[project.optional-dependencies].dev`
#      and `[dependency-groups].benchmark` in `pyproject.toml`, but only as a
#      diagnostic read surface — not an edit target by default.
# Allowed fixes under #2451 if A1b is confirmed:
#   - remove/neutralize benchmark-plugin disablement in test-job scope
#   - add explicit plugin loading only within the test job / target benchmark file
#   - if no bounded plugin-loading fix is found within these 4 inspection surfaces,
#     stop and choose A2 with an explicit tracking issue rather than continuing
#     unbounded diagnosis
# `pyproject.toml` is out of scope for edit unless execution produces a concrete,
# minimal repro proving package metadata interaction is the root cause of the missing
# `benchmark` fixture on runner; absent that proof, treat A1b as configuration/plugin
# loading only.
# Acceptance for A1b:
#   - benchmark fixture is available in the test job or benchmark tests are
#     intentionally skipped under A2 with explicit tracking
#   - no changes spill into the lint job / #2452 lane
#
# Branch A2 (fallback, defer): skip benchmark tests only when the package is
# genuinely absent on the runner and the workflow edit is either unsupported or
# out of scope for this issue.
# Add a module-top bare importorskip:
#   pytest.importorskip("pytest_benchmark")
# A2 is NOT valid when pytest_benchmark imports successfully but the fixture is
# still unavailable due to plugin-autoload suppression; that case stays in A1b.
# A2 is also explicitly an inferior outcome to A1a/A1b because it preserves CI
# stability by deferring benchmark coverage rather than restoring it. Choose A2
# only with recorded evidence that A1a/A1b could not preserve benchmark execution
# within this issue's bounded scope.
#
# Decision rule: start from A1b by default. Use A1a only after the CI log proves
# the missing-fixture error is truly caused by absent benchmark plugin availability
# on the runner.

# === Cluster B — config_with_economics fixture scope ===
# This branch is CONDITIONAL, not automatic.
# First resolve Cluster C's handling for the legacy API class, then re-run the
# targeted non-legacy tests. Only promote the fixture if a non-skipped runtime
# test still fails on missing `config_with_economics`.
#
# Option B1 (conditional preferred if still needed): create
# tests/modules/bsee/analysis/npv-data-source-comparison/conftest.py
# with the fixture at module scope so BOTH TestCashFlowComponents and
# TestProductionAPI12CashFlowMethods can consume it.
# IMPORTANT: copy the existing fixture body from lines 105-117 verbatim.
# conftest.py contents should preserve the current values exactly:
#   CAPEX = 1460000000
#   OPEX_per_bbl = 20.0
#   discount_rate_annual = 0.10
#   meta.label = "test_cash_flow"
# Then remove the in-class fixture at line 105 of test_cash_flow_components.py
# to avoid a duplicate-definition warning.
#
# Conditional gate for B1:
#   - if Cluster C-skip removes the only failing consumer and
#     `TestCashFlowComponents` still passes, do NOT create conftest.py in #2451.
#   - if a remaining non-legacy test still fails on missing fixture, apply B1.
#
# Option B2 (minimal): duplicate the fixture inside TestProductionAPI12CashFlowMethods.
# Rejected — creates drift between classes; use B1 only if fixture promotion is
# still required after Cluster C handling.

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
# Step V3a: `Test Python 3.11` is the mandatory close gate because that lane is
# directly evidenced in run 24757842396.
# Step V3b: inspect Python 3.10 / 3.12 lanes on the new run. Even if those lanes did
# not previously provide the primary evidence, perform a targeted post-fix check that
# the affected benchmark and NPV targets do not regress there after the shared test/
# workflow edits. If any of the same three #2451 signatures appear on 3.10 / 3.12,
# those lanes immediately join this issue's required verification set and must be
# cleared before closure.
# Step V3c: record a before/after failure-set comparison for the affected targets on
# 3.11 and the inspected 3.10 / 3.12 lanes so branch selection and closure are auditably
# tied to concrete signatures rather than judgment calls.
# Step V4: re-run `uv run pytest tests/ --collect-only --override-ini="addopts="`
# to ensure no new collection failures were introduced by the fixture/skip edits.
# Step V5: if rebasing the execution branch onto current worldenergydata `main`
# surfaces conflicts with the already-landed #2433 state, resolve them on the
# dedicated execution branch and re-run the targeted RED/GREEN commands. If the
# conflicts change the failure surface beyond the three #2451 clusters, STOP and
# reopen planning rather than silently broadening implementation scope.
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify (conditional) | `worldenergydata/.github/workflows/ci.yml` | (Cluster A1a only) narrow workflow edit on the `test` job install step if and only if CI-log evidence proves the runner is missing the benchmark plugin. Prefer `uv sync --all-extras --group benchmark`; fall back to `--all-groups` only if required by runner/tooling. `lint` job stays untouched — #2452 owns that lane. |
| Create (conditional) | `worldenergydata/tests/modules/bsee/analysis/npv-data-source-comparison/conftest.py` | (Cluster B1 only if still needed after Cluster C handling) module-scope `config_with_economics` fixture copied verbatim from the current in-class fixture so both classes can consume it when the legacy class remains active. |
| Modify (conditional) | `worldenergydata/tests/modules/bsee/analysis/npv-data-source-comparison/test_cash_flow_components.py` | Remove the in-class fixture only if B1 fixture promotion is needed; under the default Cluster C path, apply class-level skip only to `TestProductionAPI12CashFlowMethods`, preserving `TestCashFlowComponents` coverage. |
| Modify | `worldenergydata/tests/modules/bsee/analysis/npv-data-source-comparison/test_current_npv_implementation.py` | (Cluster C default) add collection-safe module-level `pytest.skip(..., allow_module_level=True)` before the broken legacy import, or repoint to the refactored financial module if the owner chooses C-repoint and a non-legacy entry point is later identified. |
| Modify (fallback only) | `worldenergydata/tests/benchmarks/test_eia_benchmarks.py` | Only if Cluster A2 is chosen after CI-log diagnosis and package absence is proven. Use bare `pytest.importorskip("pytest_benchmark")` at module top. |
| Create / link required tracker | `worldenergydata` follow-up issue for legacy NPV test re-enable/delete | Mandatory if Cluster C uses skip-based deferral. The skip reason strings must reference both `#2451` and the concrete worldenergydata follow-up issue number so coverage debt is governed rather than implicit. |
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
| verify_cashflow_no_duplicate_fixture | Grep for `def config_with_economics` in the test file after edit | post-edit file when B1 fixture promotion is applied | Exactly 0 hits in `test_cash_flow_components.py` (fixture only in conftest) |
| verify_legacy_npv_tracker_exists | `gh issue view <worldenergydata_tracker_id> --repo vamseeachanta/worldenergydata` plus grep skip strings for both `#2451` and that tracker id | skip-based Cluster C path | Tracker issue exists before skip lands, and every skip string references both issues |
| verify_current_npv_collection_safe | `uv run pytest tests/modules/bsee/analysis/npv-data-source-comparison/test_current_npv_implementation.py --collect-only --override-ini="addopts="` | worldenergydata with C-skip or C-repoint | No import-time collection error; file is either skipped or collects cleanly |
| verify_ci_residual_failure_set | `uv run pytest tests/ -v --tb=short --cov=src` | full CI command | The three #2451 failure signatures are absent; any remaining failures are explicitly outside this issue's scope |
| verify_ci_matrix_effect | New worldenergydata CI run on the fix SHA shows the three #2451 clusters gone from the `Test Python 3.11` job | `gh run view <id>` | No benchmark-fixture, `config_with_economics`, or legacy-NPV-import/method errors remain |
| verify_ci_matrix_no_regression_310_312 | Inspect Python 3.10 / 3.12 lanes for the affected benchmark + NPV targets after the shared edits land | `gh run view <id>` on fix run | No new benchmark/fixture/legacy-NPV regression introduced on 3.10 / 3.12; if the same three signatures appear, they are fixed before closure |

---

## Acceptance Criteria

- [ ] Exact CI command `uv run pytest tests/ -v --tb=short --cov=src` in the worldenergydata clone no longer reports the three failure signatures from the #2451 body: (1) benchmark fixture missing, (2) `config_with_economics` fixture missing, (3) legacy NPV import / missing `perform_npv_calculation` failures.
- [ ] Cross-repo execution contract is explicit before implementation: the fix lands on a dedicated worldenergydata branch (recommended `nightly/2451-worldenergydata`) and merges independently of workspace-hub planning commits; any dependency on #2433 landed state is rebased onto current worldenergydata `main` before PR creation. If that rebase surfaces conflicts, they are resolved on the execution branch and the targeted RED/GREEN checks are re-run; if the conflict resolution changes the failure surface beyond the three #2451 clusters, execution stops and the issue returns to planning instead of silently broadening scope.
- [ ] Cluster A branch is chosen only after failed-job log inspection on run `24757842396` confirms the benchmark root cause. Local provenance is also checked with `uv run --all-extras` before choosing A1a vs A1b. If a workflow edit is made, it is scoped to the `test` job only; `lint` remains untouched for #2452. A2 skip-based fallback is allowed only with recorded evidence that A1a/A1b could not preserve benchmark execution within this issue's bounded scope.
- [ ] If Cluster B remains needed after Cluster C handling, `worldenergydata/tests/modules/bsee/analysis/npv-data-source-comparison/conftest.py` exists and defines `config_with_economics` at module scope using the same values as the current in-class fixture.
- [ ] If Cluster B is activated, `test_cash_flow_components.py` no longer contains an in-class `config_with_economics` fixture definition after the edit (no duplicate shadowing).
- [ ] Cluster B is proven at runtime, not just collection: a representative `TestCashFlowComponents` test passes and the legacy class test is either skipped cleanly or passes after repoint.
- [ ] Cluster C handling is collection-safe: `test_current_npv_implementation.py` no longer errors during collection, and `test_cash_flow_components.py` preserves `TestCashFlowComponents` coverage while only the legacy-API class is skipped or repointed.
- [ ] If Cluster C uses skip-based deferral, the skip reason(s) reference `#2451` and a concrete worldenergydata follow-up issue for re-enable/delete ownership.
- [ ] GitHub CLI access is verified with concrete repo operations before execution of any branch that depends on failed-run log inspection or tracker creation: the executor can read run `24757842396` in `vamseeachanta/worldenergydata`, view workspace-hub issue `#2451`, and, for skip-based Cluster C, create/view the required worldenergydata tracker issue. If any of those repo operations fail, execution pauses and the blocker is documented on workspace-hub issue `#2451` rather than guessed around locally.
- [ ] No file under the #2433 conftest skip-set is re-introduced to the collection surface by accident (re-run `uv run pytest tests/ --collect-only --override-ini="addopts="` still reports 0 collection errors, and the skipped-path set is rechecked in execution notes).
- [ ] A worldenergydata CI run on the fix SHA shows the three #2451 failure clusters gone from the mandatory `Test Python 3.11` job.
- [ ] Python 3.10 / 3.12 lanes are also inspected for the affected benchmark + NPV targets after the shared test/workflow edits land. If the same three signatures appear there, those lanes become required close gates and are fixed before closure; if they do not, execution notes still record the no-regression inspection result.
- [ ] Remaining failures, if any, are explicitly enumerated as unrelated follow-up work rather than counted toward this issue.
- [ ] Adversarial review of this plan across ≥ 2 providers returns APPROVE or MINOR after final revisions.
- [ ] Deferred `docs/plans/README.md` indexing has an explicit owner/trigger: the workspace-hub consolidation pass that serializes parallel planning branches after this plan converges; it is intentionally not part of this branch due to branch-contention guardrails.
- [ ] `status:plan-review` label applied on #2451, with the plan comment linking this file and its review artifacts. User approval and `.planning/plan-approved/2451.md` marker remain workflow gates before any implementation commit, not deliverable proof.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | APPROVE | Plan is technically sound; remaining notes were limited to minor wording/clarification opportunities around branch gating and auditability. |
| Codex | MAJOR | Remaining blockers focused on speculative `pyproject.toml` edit scope, stronger repo-specific GitHub preflight, and tighter 3.10/3.12 no-regression verification. |
| Gemini | APPROVE | No blocking defects; only minor manual-inspection / uv-version notes. |

**Wave 8 overall result:** MAJOR — remaining objections are still verification-contract precision rather than root-cause diagnosis. This revision (1) removes `pyproject.toml` from the edit scope unless future execution produces a concrete repro that reopens planning, (2) strengthens GitHub preflight from `gh auth status` to concrete repo operations for run-log read and issue view/create capability, and (3) upgrades 3.10/3.12 from passive observation to targeted no-regression inspection after the shared edits land.

Revisions made based on review:
- Updated the review summary to the latest rerun wave.
- Strengthened Step -2 to require concrete repo-operation checks, not just auth presence.
- Re-scoped A1b so `pyproject.toml` remains diagnostic-read-only and is not an edit target under the current bounded plan.
- Added explicit targeted 3.10/3.12 no-regression inspection plus before/after failure-set recording.
- Split the matrix acceptance into separate mandatory-3.11, inspect-3.10/3.12, and residual-failure bullets.

The plan remains in `draft` pending the next rerun review wave.

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
| A — benchmark fixture | A1b plugin-loading diagnosis by default; A1a `uv sync --all-extras --group benchmark` only if CI log proves package absence on runner (`--all-groups` fallback only if required and supported by runner uv) | A2 `importorskip` test-local skip (fallback only when package absence is proven) | Failed-job log plus local `uv run --all-extras` provenance must establish whether the runner is missing the package or failing to autoload the plugin |
| B — `config_with_economics` scope | B1 module-scope conftest.py + runtime verification from both affected classes only if a non-skipped test still fails after Cluster C handling | B2 in-class duplication | Apply B1 only if a remaining non-legacy runtime test still fails on missing fixture after Cluster C handling |
| C — legacy NPV API drift | C-skip is the default implementation path once the plan is approved: module-level skip only in `test_current_npv_implementation.py`, class-level skip only on `TestProductionAPI12CashFlowMethods` in `test_cash_flow_components.py`; C-repoint remains blocked until a non-legacy replacement entry point is identified | C-repoint without entry-point discovery, C-delete (too aggressive) | User may override to C-repoint during plan approval, but absent that override the executor proceeds with C-skip + tracked follow-up issue |

This plan explicitly stops short of implementation. Implementation requires `status:plan-approved` on #2451 and a corresponding `.planning/plan-approved/2451.md` marker.
