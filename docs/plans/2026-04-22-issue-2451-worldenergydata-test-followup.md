# Plan for #2451: worldenergydata test job still fails after #2433 — benchmark fixture + legacy NPV API regressions

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-22
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2451
> **Parent execution issue:** #2433 (collection-unblock, landed at worldenergydata `0f8ac026`)
> **Parent meta issue:** #2424 (ecosystem CI health)
> **Sibling follow-up:** #2452 (flake8 debt keeping `lint` job red)
> **Review artifacts:** scripts/review/results/YYYYMMDDTHHMMSSZ-2026-04-22-issue-2451-worldenergydata-test-followup.md-plan-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code (worldenergydata at `nightly/2433-worldenergydata`, HEAD `0f8ac026`)

- Found: `worldenergydata/src/worldenergydata/bsee/analysis/production_api12.py` — post-refactor class `ProductionAPI12Analysis` (line 26). The docstring at line 37 explicitly says *"For revenue and NPV calculations, use the financial module at..."* and the class no longer contains `perform_npv_calculation`, `generate_revenue_table`, or `_npv_calculator`.
- Found: `worldenergydata/src/worldenergydata/bsee/analysis/legacy/production_api12_original.py` — pre-refactor copy retains all NPV helpers: `generate_revenue_table` (line 344), `perform_npv_calculation` (line 350), `perform_excel_aligned_npv_calculation` (line 354), and the delegating `_npv_calculator.perform_npv_calculation` call at line 216. This file is under `legacy/` and should not be treated as the canonical API.
- Found: `worldenergydata/tests/benchmarks/test_eia_benchmarks.py` lines 61 and 69 — two tests request the `benchmark` fixture from `pytest-benchmark`. Live pytest reports `fixture 'benchmark' not found`; loaded plugins are `anyio, asyncio, cov, timeout, hypothesis, Faker, dash` — no `benchmark` plugin.
- Found: `worldenergydata/tests/modules/bsee/analysis/npv-data-source-comparison/test_cash_flow_components.py` — the `config_with_economics` fixture is defined at line 105, inside class `TestCashFlowComponents` (line 31). It is consumed by two distinct classes:
  - class `TestCashFlowComponents` (methods at lines 140, 164, 316, 388) — can see the fixture
  - class `TestProductionAPI12CashFlowMethods` (line 447, test at line 455) — **cannot see the fixture** (class-scoped fixtures do not cross class boundaries)
  Both test files also import from the non-existent path `worldenergydata.modules.bsee.analysis.production_api12`.
- Found: `worldenergydata/tests/modules/bsee/analysis/npv-data-source-comparison/test_current_npv_implementation.py:23` — `from worldenergydata.modules.bsee.analysis.production_api12 import (ProductionAPI12Analysis)`. This import path does not exist on main; the real path is `worldenergydata.bsee.analysis.production_api12` (no `.modules` prefix).
- Found: `worldenergydata/pyproject.toml`
  - Line 60–75 `[project.optional-dependencies] dev = [...]` — contains `"pytest-benchmark>=4.0"` (line 68).
  - Line 213–216 `[dependency-groups] benchmark = [...]` — contains `"pytest-benchmark>=4.0.0,<5.0.0"` (line 215). This is PEP 735 dependency-group declaration.
- Found: `worldenergydata/.github/workflows/ci.yml` — `test` job installs via `uv sync --all-extras` (line 38) and runs `uv run pytest tests/ -v --tb=short --cov=src ...`. `--all-extras` installs optional-dependencies but does **not** install PEP 735 dependency-groups unless `--all-groups` / `--group <name>` is also passed.
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
`--all-extras` installs `[project.optional-dependencies]` but **not** `[dependency-groups]`. If `uv sync --all-extras` is picking up `dev` (which declares `pytest-benchmark>=4.0`), the fixture should be available. The local reproduction above is from a worktree `.venv` that was not synced with `--all-extras`; the *CI* failure source for the benchmark fixture must be re-confirmed in implementation by pulling the failing job log. If CI in fact installs `dev` and still misses the fixture, the real root cause is a different sync/plugin-load issue (e.g. duplicate/competing declarations across `optional-dependencies` and `dependency-groups`) and the fix must be re-scoped accordingly.

<!-- Verification: 6 distinct sources — (1) issue #2451 body, (2) issue #2433 execution comment, (3) worldenergydata repo code at SHA 0f8ac026, (4) worldenergydata pyproject.toml, (5) worldenergydata ci.yml, (6) live pytest reproduction. Minimum 3 required. Current count: 6 -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-22-issue-2451-worldenergydata-test-followup.md` |
| Plan review — Claude | `scripts/review/results/YYYYMMDDTHHMMSSZ-2026-04-22-issue-2451-worldenergydata-test-followup.md-plan-claude.md` |
| Plan review — Codex | `scripts/review/results/YYYYMMDDTHHMMSSZ-2026-04-22-issue-2451-worldenergydata-test-followup.md-plan-codex.md` |
| Plan review — Gemini | `scripts/review/results/YYYYMMDDTHHMMSSZ-2026-04-22-issue-2451-worldenergydata-test-followup.md-plan-gemini.md` |
| Implementation (cluster A) | `worldenergydata/.github/workflows/ci.yml` (install step) **or** `worldenergydata/tests/conftest.py` (skip if plugin absent) — decided at implementation time |
| Implementation (cluster B) | `worldenergydata/tests/modules/bsee/analysis/npv-data-source-comparison/conftest.py` (promote fixture) **or** in-file move to module scope |
| Implementation (cluster C) | `worldenergydata/tests/modules/bsee/analysis/npv-data-source-comparison/test_current_npv_implementation.py` + `test_cash_flow_components.py` — skip/xfail/repoint decision per cluster-C branch below |
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
gh run view <run_id> --repo vamseeachanta/worldenergydata --log-failed \
    | grep -A5 "fixture 'benchmark' not found"
# If CI log shows the same benchmark failure: the --all-extras install is not
# picking up dev group's pytest-benchmark declaration. Proceed with Cluster-A
# fix. If CI log instead shows a different error (import, collection, version),
# re-scope Cluster A before continuing.

# === Cluster A — benchmark fixture ===
# Branch A1 (preferred, fix-now): guarantee plugin on CI
# Edit .github/workflows/ci.yml Install dependencies step to:
#   run: uv sync --all-extras --all-groups
# This installs both optional-dependencies and PEP 735 dependency-groups.
#
# Branch A2 (fallback, defer): skip benchmark tests when plugin absent
# Add a module-level pytest skip marker to tests/benchmarks/test_eia_benchmarks.py:
#   pytest_benchmark = pytest.importorskip("pytest_benchmark")
# This preserves the tests for later without requiring the plugin.
#
# Decision rule: prefer A1 unless CI log shows the fix is more invasive than
# a one-line install change. Record the decision in the commit message.

# === Cluster B — config_with_economics fixture scope ===
# Option B1 (preferred): create tests/modules/bsee/analysis/npv-data-source-comparison/conftest.py
#   with the fixture at module scope so BOTH TestCashFlowComponents and
#   TestProductionAPI12CashFlowMethods can consume it.
# conftest.py contents:
#   import pytest
#   @pytest.fixture
#   def config_with_economics():
#       return { "economics": { "cost": {
#           "CAPEX": 1_460_000_000,
#           "OPEX_per_bbl": 20.0,
#           "discount_rate_annual": 0.10,
#       }}, "meta": {"label": "test_cash_flow"} }
# Then remove the in-class fixture at line 105 of test_cash_flow_components.py
# to avoid a duplicate-definition warning.
#
# Option B2 (minimal): duplicate the fixture inside TestProductionAPI12CashFlowMethods.
# Rejected — creates drift between classes; B1 is the cleaner fix.

# === Cluster C — legacy NPV API / import-path drift ===
# The tests import from `worldenergydata.modules.bsee.analysis.production_api12`
# and call `perform_npv_calculation`. Neither the path nor the method exist in
# the refactored code. Choose between three sub-paths — the decision MUST be
# user-confirmed before implementation.
#
# Sub-path C-repoint (keep tests): repoint imports to the new path and call site
#   - Grep the repo for the post-refactor NPV entry point
#       (likely under src/worldenergydata/bsee/analysis/financial/ or
#        src/worldenergydata/financial/)
#   - Update the two test files' `from ... import ProductionAPI12Analysis` (or
#     the replacement) and adjust method calls to the new API signature
#   - Update test assertions if the return shape changed
#   - Risk: the refactor may have deliberately dropped the method (e.g.
#     collapsed into a helper); repointing may not be mechanical
#
# Sub-path C-skip (track-and-move-on): mark both files with module-level
# pytest.skip and link the issue
#     pytestmark = pytest.mark.skip(
#         reason="Legacy NPV API — refactored module no longer exposes "
#         "perform_npv_calculation. Tracked in #2451 follow-up."
#     )
#   - Consistent with #2433 conftest skip-list pattern
#   - Leaves the residual failures cleanly attributed
#
# Sub-path C-delete (aggressive): remove the two files entirely, since the
# legacy method they cover has been deprecated out of the production API.
#   - Rejected as default because test-preservation is cheaper than
#     test-rewriting if the decision is later reversed.
#
# Recommended default: C-skip. Fast, reversible, matches #2433 precedent,
# and avoids committing workspace-hub planning effort to a worldenergydata
# API-surface decision that belongs to the module owner.

# === Verification Phase (GREEN) ===

# Step V1: re-run each cluster's pytest command from Step 0 and confirm the
# failure signature is gone (either PASSED or SKIPPED, not ERROR).
# Step V2: run the full CI command locally:
#   uv run pytest tests/ -v --tb=short --cov=src
# Expected: residual failure count from the pre-fix baseline drops by
# at least the 3 clusters targeted here. Remaining failures (if any) are
# logged for follow-up; this plan does NOT commit to restoring every test.
# Step V3: push the fix branch and confirm the matrix job on run <new_id>
# at worldenergydata SHA <new_sha>.
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `worldenergydata/.github/workflows/ci.yml` | (Cluster A1) change `uv sync --all-extras` to `uv sync --all-extras --all-groups` so PEP 735 `[dependency-groups] benchmark` installs `pytest-benchmark`. Applies to both `test` and `lint` job install steps for symmetry. |
| Create | `worldenergydata/tests/modules/bsee/analysis/npv-data-source-comparison/conftest.py` | (Cluster B1) module-scope `config_with_economics` fixture so both `TestCashFlowComponents` and `TestProductionAPI12CashFlowMethods` can consume it. |
| Modify | `worldenergydata/tests/modules/bsee/analysis/npv-data-source-comparison/test_cash_flow_components.py` | (Cluster B1) remove now-redundant in-class fixture at line 105; (Cluster C default) add `pytestmark = pytest.mark.skip(...)` referencing #2451 until the refactored NPV API surface is mapped. |
| Modify | `worldenergydata/tests/modules/bsee/analysis/npv-data-source-comparison/test_current_npv_implementation.py` | (Cluster C default) add `pytestmark = pytest.mark.skip(...)` referencing #2451 until import path and method repoint are decided by module owner. |
| (Alternative only, Cluster A2) Modify | `worldenergydata/tests/benchmarks/test_eia_benchmarks.py` | Only if Cluster A1 is rejected at implementation time. Replace with `pytest_benchmark = pytest.importorskip("pytest_benchmark")` at module top. |
| Update (deferred, not this run) | `docs/plans/README.md` | Plan index row. Intentionally **not** edited in the nightly/2451-plan branch per the branch-contention guard — performed in a later consolidation run. |

---

## TDD Test List

This is a cross-repo infrastructure / test-hygiene fix. "Tests" here are verification commands executed against the `worldenergydata` clone; no new pytest files in workspace-hub.

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| verify_benchmark_cluster_resolved | `uv run pytest tests/benchmarks/test_eia_benchmarks.py --override-ini="addopts="` no longer reports `fixture 'benchmark' not found` | worldenergydata with A1 (or A2) applied | Exit code 0 for A1 (tests pass) or SKIPPED line for A2 |
| verify_benchmark_plugin_loaded | `uv run pytest --version` header includes `pytest-benchmark` plugin | worldenergydata with A1 applied | Plugin list contains `benchmark-X.Y.Z` |
| verify_cashflow_fixture_resolved | `uv run pytest tests/modules/bsee/analysis/npv-data-source-comparison/test_cash_flow_components.py --collect-only --override-ini="addopts="` no longer reports `fixture 'config_with_economics' not found` | worldenergydata with B1 applied | No fixture-missing errors at collection |
| verify_cashflow_no_duplicate_fixture | Grep for `@pytest.fixture[\s\S]*def config_with_economics` in the test file after edit | post-edit file | Exactly 0 hits (fixture only in conftest) |
| verify_npv_import_resolvable_or_skipped | `python -c "import worldenergydata.modules.bsee.analysis.production_api12"` resolves **or** module-level `pytestmark` skip applies | worldenergydata with C-repoint or C-skip | ModuleNotFoundError disappears (repoint) OR pytest emits SKIPPED with reason string including `#2451` (skip) |
| verify_ci_residual_failure_set_shrinks | `uv run pytest tests/ -v --tb=short --cov=src` residual failure count drops by at least the three clusters vs pre-fix baseline | full CI command | Post-fix failure count < pre-fix failure count by ≥ (N benchmark + M cashflow + K currentnpv) tests |
| verify_ci_matrix_effect | New worldenergydata CI run on the fix SHA shows `Test Python 3.11` job either green or explicitly reduced | `gh run view <id>` | Job matrix reflects expected delta; no new failures introduced |

---

## Acceptance Criteria

- [ ] Exact CI command `uv run pytest tests/ -v --tb=short --cov=src` in the worldenergydata clone no longer reports the three failure signatures from the #2451 body (benchmark fixture, config_with_economics fixture, legacy NPV `perform_npv_calculation` / `modules.bsee` import).
- [ ] `worldenergydata/.github/workflows/ci.yml` install step either installs `pytest-benchmark` (Cluster A1) or the test file skip marker renders the benchmark tests SKIPPED not ERROR (Cluster A2).
- [ ] `worldenergydata/tests/modules/bsee/analysis/npv-data-source-comparison/conftest.py` exists and defines `config_with_economics` at module scope (Cluster B1).
- [ ] `test_cash_flow_components.py` no longer contains an in-class `config_with_economics` fixture definition after the edit (no duplicate shadowing).
- [ ] The two NPV test files are either repointed to the refactored financial module with passing assertions (Cluster C-repoint) **or** carry a module-level `pytestmark = pytest.mark.skip(reason=...)` that references #2451 (Cluster C-skip).
- [ ] No file under the #2433 conftest skip-set is re-introduced to the collection surface by accident (re-run `uv run pytest tests/ --collect-only --override-ini="addopts="` still reports 0 collection errors).
- [ ] A worldenergydata CI run on the fix SHA completes with a strictly smaller `Test` job failure surface than run `24757842396`. Remaining failures are enumerated and tracked via follow-up issue(s).
- [ ] Adversarial review of this plan across ≥ 2 providers returns APPROVE or MINOR after final revisions.
- [ ] `status:plan-review` label applied on #2451, with the plan comment linking this file and its review artifacts.
- [ ] User approval recorded (`status:plan-approved` label + `.planning/plan-approved/2451.md` marker) **before** any implementation commit.

---

## Adversarial Review Summary

<!-- Filled after Step 4. Plan is currently in draft status; no review artifacts exist yet. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | — |
| Codex | PENDING | — |
| Gemini | PENDING | — |

**Overall result:** PENDING — plan is draft-only. Do not surface for user approval until at least two providers have run adversarially (attested-evidence mode) and all MAJOR findings are resolved.

Revisions made based on review:
- (none yet)

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
| A — benchmark fixture | A1 `uv sync --all-extras --all-groups` in ci.yml | A2 `importorskip` test-local skip (fallback only) | CI job log must confirm same `fixture not found` on runner before A1 edit lands |
| B — `config_with_economics` scope | B1 module-scope conftest.py | B2 in-class duplication | None — single-file additive change; safe |
| C — legacy NPV API drift | C-skip (module-level `pytestmark.skip` with #2451 reason string) | C-repoint (requires financial-module audit), C-delete (too aggressive) | User confirmation required during plan-review; C-skip is the conservative default but user may override to C-repoint if they want the coverage restored now |

This plan explicitly stops short of implementation. Implementation requires `status:plan-approved` on #2451 and a corresponding `.planning/plan-approved/2451.md` marker.
